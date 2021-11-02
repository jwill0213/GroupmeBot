import os
import sys
import requests
from importlib import import_module
from flask import Flask, request
from enum import Enum

#######################################################################################################
######################## Customization ################################################################

'''
The bot will automatically log certain items, and log other items when DEBUG is set.
Some command lines might not show colors well, or they may overlap with your theme.
You can change the appearance of entries by replacing these values with other ANSI codes.
'''


class logType(Enum):
    SEVERE = '\033[31m[ SEVERE ]\033[00m '  # if something critical is caught
    WARN = '\033[33m[ WARN ]\033[0m '  # not critical, but still bad
    # something good happens that might not always happen
    OK = '\033[32m[ OK ]\033[00m '
    # prefix for log entries when debugging
    DEBUG = '\033[35m[ BOT-DEBUG ]\033[00m '
    LOG = '\033[36m[ BOT-LOG ]\033[00m '  # prefix for all other log entries
    USRMSG = '\033[36m[ MESSAGE ]\033[00m '  # prefix for captured messages
    # prefix for messages by the bot (  i.e. [ MESSAGE ] [ BOT ] Botname: Message  )
    BOTMSG = '\033[33m[ BOT MSG ]\033[00m '
    # Same as above, but for system messages like topic changes
    SYSMSG = '\033[00m[ GroupMe ]\033[00m '


class LOGGER:
    # suffix for log entries (normally just clears formatting)
    logTail = '\033[00m'

    @staticmethod
    def warn(msg):
        print(logType.WARN.value + msg + LOGGER.logTail)

    @staticmethod
    def severe(msg):
        print(logType.SEVERE.value + msg + LOGGER.logTail)

    @staticmethod
    def ok(msg):
        print(logType.OK.value + msg + LOGGER.logTail)

    @staticmethod
    def debug(msg):
        print(logType.DEBUG.value + msg + LOGGER.logTail)

    @staticmethod
    def log(msg):
        print(logType.LOG.value + msg + LOGGER.logTail)

    @staticmethod
    def userMsg(msg):
        print(logType.USRMSG.value + msg + LOGGER.logTail)

    @staticmethod
    def botmsg(msg):
        print(logType.BOTMSG.value + msg + LOGGER.logTail)

    @staticmethod
    def sysmsg(msg):
        print(logType.SYSMSG.value + msg + LOGGER.logTail)

#######################################################################################################
######################## Initialization ###############################################################


# To enable debugging the hard way, type 'True #' after 'Debug = '
DEBUG = (True if os.getenv('BOT_DEBUG') == 'True' else False)
POST_TO = 'https://api.groupme.com/v3/bots/post'
GROUP_RULES = {}
BOT_INFO = {}

if DEBUG:
    LOGGER.debug("Web concurrency is set to " + os.getenv('WEB_CONCURRENCY'))
    if os.getenv('WEB_CONCURRENCY') != '1':
        LOGGER.debug(
            "NOTE: When debugging with concurrency, you may see repetitive log entries.")

# Parses bot data from the environment into the format { group_id : [bot_id, bot_name, bot_alias] }
for bot in (os.getenv('BOT_INFO')).split('; '):
    info = bot.split(', ')
    BOT_INFO[info[0]] = (info[1], info[2], info[3])

LOGGER.ok(f"FOUND BOTS: {BOT_INFO}")

# When you create global rules for the bot, they will be imported here.
try:
    # TODO Change to importlib.import_module
    GLOBAL_RULES = import_module('global_rules')
    LOGGER.ok("Global rules found and added.")
except ImportError:
    LOGGER.warn(
        "Global rules not found. Bot may load, but it won't do anything.")

# When you create custom rules for a group, they will be imported here.
for group in BOT_INFO:
    try:
        groupAlias = BOT_INFO[group][2]
        GROUP_RULES[group] = import_module('group_{}'.format(groupAlias))
        LOGGER.ok("Group rules found and added for [G:{}]".format(group))
    except ImportError:
        if group in GROUP_RULES:
            del GROUP_RULES[group]
        if DEBUG:
            LOGGER.debug("Group rules not found for [G:{}]".format(group))

#######################################################################################################
######################## Helper functions #############################################################


def attach_type(attachments):
    types = {
        'image': '[IMG] ',
        'location': '[LOC] ',
        'poll': '',
        'event': ''
    }
    typelist = ''
    for attachment in attachments:
        try:
            typelist += types[attachment['type']]
        except KeyError:
            LOGGER.warn('Attachment type {} unknown.'.format(
                attachment['type']))
    return typelist

# TODO Make log entries for polls and events appear cleaner (not critical)


def logmsg(data):
    try:
        sender_type = data['sender_type']
    except KeyError as missing_key:
        LOGGER.warn("Message data does not contain a sender_type.")
    else:
        if sender_type == 'user':
            LOGGER.userMsg("{}: {}{}".format(
                data['name'], attach_type(data['attachments']), data['text']))
        elif sender_type == 'system':
            LOGGER.sysmsg(data['text'])
        elif sender_type == 'bot':
            LOGGER.botmsg("{}: {}{}".format(data['name'], attach_type(
                data['attachments']), data['text']))


def send_message(msg, bot_id):
    data = {
        'bot_id': bot_id,
        'text': msg,
    }
    requests.post(POST_TO, json=data)

#######################################################################################################
######################## The actual bot ###############################################################


app = Flask(__name__)


@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()

    logmsg(data)

    # Prevent the bot from acting on its own messages
    if data['name'] == BOT_INFO[data['group_id']][1]:
        return "ok", 200

    if data['group_id'] in GROUP_RULES:
        try:
            if GROUP_RULES[data['group_id']].run(data, BOT_INFO[data['group_id']], send_message):
                LOGGER.ok("Group rule run successfully")
        except Exception as e:
            cmd, args = data['text'].split(' ')
            errorMsg = f"Tried to run {data['group_id']} rule '{cmd}' "
            if len(args) > 0:
                errorMsg += f'with arguments {args} '
            errorMsg += "but failed with an exception:" + e
            LOGGER.severe(errorMsg)

    try:
        if GLOBAL_RULES.run(data, BOT_INFO[data['group_id']], send_message):
            LOGGER.ok("Global rule run successfully")
    except Exception as e:
        cmd, args = data['text'].split(' ')
        errorMsg = f"Tried to run global rule '{cmd}' "
        if len(args) > 0:
            errorMsg += f'with arguments {args} '
        errorMsg += "but failed with an exception:" + e
        LOGGER.severe(errorMsg)

    return "ok", 200


@app.route('/', methods=['GET'])
def hello():
    return "Hello! This app is empty and has no UI", 200
