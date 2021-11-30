import logging
from Utils.cryptoUtils import DuplicateSymbolException, addToWatchlist, findCryptoInfoCMC, findPriceString, getPricesForWatchlist, findCoin, removeDefault, removeFromWatchlist

from Utils.questionUtils import answerQuestion, askQuestion


def run(data, botID, send):
    message = data['text']

    cmd, *args = message.split(' ')

    try:
        if cmd == '!price':
            coinData = findCoin(args, defaultSymbol='SHIB')
            send(findPriceString(coinData), botID)
            return True
        if cmd == "!info":
            coinData = findCoin(args, defaultSymbol='SHIB')
            send(findCryptoInfoCMC(coinData), botID)
            return True
        if cmd == "!watch":
            coinData = findCoin(args)
            if coinData:
                send(addToWatchlist(coinData, botID), botID)
                return True
            else:
                send(getPricesForWatchlist(botID), botID)
                return True
        if cmd == "!removeWatch":
            coinData = findCoin(args)
            if coinData:
                send(removeFromWatchlist(coinData, botID), botID)
                return True
        if cmd == "!watchlist":
            send(getPricesForWatchlist(botID), botID)
            return True
        if cmd == "!pick":
            selection = int(args[0])
            send(answerQuestion(selection, botID), botID)
            return True
        if cmd == "!removeDefault":
            coinData = findCoin(args)
            send(removeDefault(coinData['symbol']), botID)
            return True
    except DuplicateSymbolException as e:
        (questionObject,) = e.args
        logging.warning(
            f"Multiple coins found with the same symbol. {questionObject}")
        send(askQuestion(questionObject, botID), botID)
    except Exception:
        logging.error(
            f"Unhandled exception with command {data}", exc_info=True)
        send("Problem executing your command. Paging ", botID, [
             {'tag': '@Jordan Williams', 'id': 7405778}])

    return False
