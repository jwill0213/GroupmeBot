import requests
import logging

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
            logging.warning('Attachment type {} unknown.'.format(
                attachment['type']))
    return typelist


def send_message(msg, bot_id, mentions=None):
    data = {
        'bot_id': bot_id,
        'text': msg,
    }
    if mentions:
        data['attachments'] = [
            {
                "loci": [],
                "type": "mentions",
                "user_ids": []
            }
        ]
        for mention in mentions:
            startIndex = len(msg) - 1
            data['text'] = data['text'] + mention['tag']
            data['attachments'][0]['loci'].append(
                [startIndex, len(mention['tag'])])
            data['attachments'][0]['user_ids'].append(mention['id'])
            pass

    requests.post(POST_TO, json=data)
