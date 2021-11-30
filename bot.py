import os
import logging
from importlib import import_module
from flask import Flask, request
from time import sleep
from pytz import timezone, utc
from datetime import datetime

from Utils.groupmeUtils import send_message, attach_type

# To enable debugging the hard way, type 'True #' after 'Debug = '
DEBUG_LEVEL = (logging.DEBUG if os.getenv(
    'BOT_DEBUG') == 'True' else logging.WARNING)
GROUP_RULES = {}
BOT_INFO = {}
ADMIN_IDS = [7405778]


def customTime(*args):
    utc_dt = utc.localize(datetime.utcnow())
    my_tz = timezone("US/Central")
    converted = utc_dt.astimezone(my_tz)
    return converted.timetuple()


logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=DEBUG_LEVEL)

logging.Formatter.converter = customTime

logging.debug("Web concurrency is set to " + os.getenv('WEB_CONCURRENCY'))
if os.getenv('WEB_CONCURRENCY') != '1':
    logging.debug(
        "NOTE: When debugging with concurrency, you may see repetitive log entries.")

# Parses bot data from the environment into the format { group_id : [bot_id, bot_name, bot_alias] }
for bot in (os.getenv('BOT_INFO')).split('; '):
    info = bot.split(', ')
    BOT_INFO[info[0]] = (info[1], info[2], info[3])

logging.info(f"FOUND BOTS: {BOT_INFO}")

# When you create global rules for the bot, they will be imported here.
try:
    GLOBAL_RULES = import_module('Rules.globalRules')
    logging.info("Global rules found and added.")
except ImportError:
    logging.warning(
        "Global rules not found. Bot may load, but it won't do anything.", exc_info=True)

# When you create custom rules for a group, they will be imported here.
for group in BOT_INFO:
    try:
        botID = BOT_INFO[group][0]
        botName = BOT_INFO[group][1]
        groupAlias = BOT_INFO[group][2]
        GROUP_RULES[group] = import_module(f'Rules.{groupAlias}')
        logging.info(
            f"Group rules ({groupAlias}) found and added for [{botName}:{botID}]")
    except ImportError:
        if group in GROUP_RULES:
            del GROUP_RULES[group]
        logging.debug(
            f"Group rules ({groupAlias}) not found for [{botName}:{botID}].", exc_info=True)


def logmsg(data):
    try:
        sender_type = data['sender_type']
    except KeyError:
        logging.warning(
            "Message data does not contain a sender_type.", exc_info=True)
    else:
        if sender_type == 'user':
            logging.info(
                f"[ GroupMe ] {data['name']}({data['user_id']}): {attach_type(data['attachments'])}{data['text']}")
        elif sender_type == 'system':
            logging.info(f"[ MESSAGE ] {data['text']}")
        elif sender_type == 'bot':
            logging.info(
                f"[ BOT MSG ] {data['name']}: {data['attachments']}{data['text']}")


app = Flask(__name__)


@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    groupID = data['group_id']
    botID = BOT_INFO[groupID][0]

    logmsg(data)

    # Add a sleep to make sure the bot message is after the command message
    sleep(1)

    # Prevent the bot from acting on its own messages or if there is no command prefix on the message
    if data['name'] == BOT_INFO[groupID][1] or data['text'][0] != '!':
        return "ok", 200

    try:
        if groupID in GROUP_RULES and GROUP_RULES[groupID].run(data, botID, send_message):
            logging.info("Group rule run successfully")
        elif GLOBAL_RULES.run(data, BOT_INFO[groupID], send_message):
            logging.info("Global rule run successfully")
        else:
            logging.info(f"No rules found for {data['text']}")
    except Exception as e:
        if len(data['text'].split(' ')) > 1:
            cmd, args = data['text'].split(' ')
        else:
            cmd = data['text']
            args = []
        errorMsg = f"Tried to run {groupID} rule '{cmd}' "
        if len(args) > 0:
            errorMsg += f'with arguments {args} '
        errorMsg += "but failed with an exception:" + str(e)
        logging.error(errorMsg, exc_info=True)

    return "ok", 200


@app.route('/', methods=['GET'])
def hello():
    return "Hello! This app is empty and has no UI", 200
