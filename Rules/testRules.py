import logging

from Utils.cryptoUtils import DuplicateSymbolException, addToWatchlist, findCryptoInfoCMC, findPriceString, getPricesForWatchlist, findCoin, removeDefault, removeFromWatchlist

from Utils.questionUtils import answerQuestion, askQuestion


def run(data, botID, send):
    message = data['text']

    cmd, *args = message.split(' ')

    try:
        match message.split(' '):
            case ['!price', *args]:
                coinData = findCoin(args, defaultSymbol='SHIB')
                send(findPriceString(coinData), botID)
                return True
            case ['!info', *args]:
                coinData = findCoin(args, defaultSymbol='SHIB')
                send(findCryptoInfoCMC(coinData), botID)
                return True
            case ['!watch', *args]:
                coinData = findCoin(args)
                if coinData:
                    send(addToWatchlist(coinData, botID), botID)
                    return True
                else:
                    send(getPricesForWatchlist(botID), botID)
                    return True
            case ['!removeWatch', *args]:
                coinData = findCoin(args)
                if coinData:
                    send(removeFromWatchlist(coinData, botID), botID)
                    return True
            case ['!watchlist']:
                send(getPricesForWatchlist(botID), botID)
                return True
            case ['!removeDefault', *args]:
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
