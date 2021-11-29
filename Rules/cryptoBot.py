from Utils.cryptoUtils import DuplicateSymbolException, addToWatchlist, findCryptoInfoCMC, findPrice, getPricesForWatchlist, getSymbol, removeFromWatchlist
from Utils.loggerUtils import LOGGER


def run(data, bot_info, send):
    message = data['text']

    cmd, *args = message.split(' ')

    try:
        if cmd == '!price':
            symbol = getSymbol(args)
            send(findPrice(symbol), bot_info[0])
            return True
        if cmd == "!info":
            symbol = getSymbol(args)
            send(findCryptoInfoCMC(symbol), bot_info[0])
            return True
        if cmd == "!watch":
            symbol = getSymbol(args)
            try:
                send(addToWatchlist(symbol, bot_info[0]), bot_info[0])
                return True
            except Exception as e:
                LOGGER.severe(e)
        if cmd == "!removeWatch":
            symbol = getSymbol(args)
            try:
                send(removeFromWatchlist(symbol, bot_info[0]), bot_info[0])
                return True
            except Exception as e:
                LOGGER.severe(e)
        if cmd == "!watchlist":
            send(getPricesForWatchlist(bot_info[0]), bot_info[0])
            return True
    except DuplicateSymbolException as e:
        LOGGER.warn(f"Multiple coins found with the same symbol. {e}")

    return False
