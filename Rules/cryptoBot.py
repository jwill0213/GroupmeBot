from Utils.cryptoUtils import findPrice


def run(data, bot_info, send):
    message = data['text']

    cmd, *args = message.split(' ')

    if cmd == '!price':
        send(findPrice(args), bot_info[0])
        return True

    return False
