import requests

from Utils.loggerUtils import LOGGER


POST_TO = 'https://api.groupme.com/v3/bots/post'


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


def send_message(msg, bot_id):
    data = {
        'bot_id': bot_id,
        'text': msg,
    }
    requests.post(POST_TO, json=data)
