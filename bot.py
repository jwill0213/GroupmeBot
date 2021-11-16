import os
from importlib import import_module
from flask import Flask, request
from time import sleep

from Utils.groupmeUtils import send_message, attach_type
from Utils.loggerUtils import LOGGER


# To enable debugging the hard way, type 'True #' after 'Debug = '
DEBUG = (True if os.getenv('BOT_DEBUG') == 'True' else False)
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
    GLOBAL_RULES = import_module('Rules.allBots')
    LOGGER.ok("Global rules found and added.")
except ImportError:
    LOGGER.warn(
        "Global rules not found. Bot may load, but it won't do anything.")

# When you create custom rules for a group, they will be imported here.
for group in BOT_INFO:
    try:
        groupAlias = BOT_INFO[group][2]
        GROUP_RULES[group] = import_module('Rules.{}'.format(groupAlias))
        LOGGER.ok("Group rules found and added for [G:{}]".format(groupAlias))
    except ImportError as e:
        if group in GROUP_RULES:
            del GROUP_RULES[group]
        if DEBUG:
            LOGGER.debug("Group rules not found for [G:{}]. {}".format(
                groupAlias, str(e)))


def logmsg(data):
    try:
        sender_type = data['sender_type']
    except KeyError:
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


app = Flask(__name__)


@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()

    logmsg(data)

    # Add a sleep to make sure the bot message is after the command message
    sleep(1)

    # Prevent the bot from acting on its own messages
    if data['name'] == BOT_INFO[data['group_id']][1]:
        return "ok", 200

    if data['group_id'] in GROUP_RULES:
        try:
            if GROUP_RULES[data['group_id']].run(data, BOT_INFO[data['group_id']], send_message):
                LOGGER.ok("Group rule run successfully")
        except Exception as e:
            if len(data['text'].split(' ')) > 1:
                cmd, args = data['text'].split(' ')
            else:
                cmd = data['text']
                args = []
            errorMsg = f"Tried to run {data['group_id']} rule '{cmd}' "
            if len(args) > 0:
                errorMsg += f'with arguments {args} '
            errorMsg += "but failed with an exception:" + str(e)
            LOGGER.severe(errorMsg)

    try:
        if GLOBAL_RULES.run(data, BOT_INFO[data['group_id']], send_message):
            LOGGER.ok("Global rule run successfully")
    except Exception as e:
        if len(data['text'].split(' ')) > 1:
            cmd, args = data['text'].split(' ')
        else:
            cmd = data['text']
            args = []
        errorMsg = f"Tried to run global rule '{cmd}' "
        if len(args) > 0:
            errorMsg += f'with arguments {args} '
        errorMsg += "but failed with an exception:" + str(e)
        LOGGER.severe(errorMsg)

    return "ok", 200


@app.route('/', methods=['GET'])
def hello():
    return "Hello! This app is empty and has no UI", 200
