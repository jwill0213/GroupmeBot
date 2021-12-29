import logging

from Utils.cryptoUtils import DuplicateSymbolException, addToWatchlist, findCryptoInfoCMC, findPriceString, getSpreadsheetLink, getWatchlistPriceString, findCoin, removeDefault, removeFromWatchlist

from Utils.questionUtils import answerQuestion, askQuestion


def run(data, botID, send):
    message = data['text']

    try:
        match message.split(' '):
            case ['!price', *args]:
                coinData = findCoin(args, botID, defaultSymbol='SHIB')
                send(findPriceString(coinData), botID)
                return True
            case ['!info', *args]:
                coinData = findCoin(args, botID, defaultSymbol='SHIB')
                send(findCryptoInfoCMC(coinData), botID)
                return True
            case ['!watch', *args]:
                coinData = findCoin(args, botID)
                if coinData:
                    send(addToWatchlist(coinData, botID), botID)
                    return True
                else:
                    send(getWatchlistPriceString(botID), botID)
                    return True
            case ['!removeWatch', *args]:
                coinData = findCoin(args, botID)
                if coinData:
                    send(removeFromWatchlist(coinData, botID), botID)
                    return True
            case ['!watchlist']:
                send(getWatchlistPriceString(botID), botID)
                return True
            case ['!removeDefault', *args]:
                coinData = findCoin(args, botID)
                send(removeDefault(coinData['symbol']), botID)
                return True
            case ['!pick', *args]:
                selection = int(args[0])
                send(answerQuestion(selection, botID), botID)
                return True
            case ['!spreadsheet']:
                spreadsheetUrl = getSpreadsheetLink(botID)
                if spreadsheetUrl:
                    send(
                        f'Crypto Data Spreadsheet is here {spreadsheetUrl}.', botID)
                else:
                    send(
                        'There is no crypto data spreadsheet setup for this group.', botID)
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
