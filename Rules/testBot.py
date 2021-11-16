from Utils.cryptoUtils import findCryptoInfo, findCryptoInfoCMC, findPrice


def run(data, bot_info, send):
    message = data['text']

    cmd, *args = message.split(' ')

    if cmd == '!price':
        send(findPrice(args), bot_info[0])
        return True
    if cmd == "!info":
        send(findCryptoInfoCMC(args), bot_info[0])
        return True

    return False
