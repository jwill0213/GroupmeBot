import os
import pytz
import math
import json
import logging

from datetime import datetime

from Utils.redisUtils import getRedisClient

from coinmarketcapapi import CoinMarketCapAPI, CoinMarketCapAPIError
from bs4 import BeautifulSoup as bs
import requests

BASE_CMC_URL = "https://coinmarketcap.com/currencies/"


def addToWatchlist(coinData, botID):
    r = getRedisClient()
    if r.hexists(botID, "watchlist"):
        watchlist = json.loads(r.hget(botID, "watchlist"))
        if len([w for w in watchlist if w["symbol"] == coinData["symbol"]]) == 0:
            watchlist.append(coinData)
            newWatchlist = json.dumps(watchlist)
            r.hset(botID, "watchlist", newWatchlist)
            logging.debug(f"NEW WATCHLIST: {newWatchlist}")
            return f"Added {coinData['symbol']} | {coinData['name']} to the watchlist."
        else:
            return f"{coinData['symbol']} | {coinData['name']} is already on the watchlist."
    else:
        newWatchlist = json.dumps([coinData])
        r.hset(botID, "watchlist", newWatchlist)


def removeFromWatchlist(coinData, botID):
    r = getRedisClient()
    if r.hexists(botID, "watchlist"):
        watchlist = json.loads(r.hget(botID, "watchlist"))
        newWatchlist = [w for w in watchlist if w["symbol"] != coinData["symbol"]]
        if len(newWatchlist) < len(watchlist):
            r.hset(botID, "watchlist", json.dumps(newWatchlist))
            logging.debug(f"NEW WATCHLIST: {newWatchlist}")
            return (
                f"Removed {coinData['symbol']} | {coinData['name']} from the watchlist."
            )
        elif len(newWatchlist) == len(watchlist):
            return f"{coinData['symbol']} | {coinData['name']} is not on the watchlist."
    else:
        return f"{coinData['symbol']} | {coinData['name']} is not on the watchlist."


def getPriceDataForWatchlist(botID):
    r = getRedisClient()
    if r.hexists(botID, "watchlist"):
        watchlist = json.loads(r.hget(botID, "watchlist"))
        logging.debug(watchlist)

        return getQuoteFromCMC(watchlist)
    else:
        return None


def getWatchlistPriceString(botID):
    priceData = getPriceDataForWatchlist(botID)

    if priceData is not None:
        logging.debug(priceData)

        stringList = [f"Prices for watchlist as of {priceData['dataDate']}"]
        for symbol, quoteData in priceData["quotes"].items():
            change24 = quoteData["percent_change_24h"]
            change24 = change24[: change24.index("%") + 1]
            if "+" in change24:
                change24 += "🟢"
            elif "-" in change24:
                change24 += "🔴"
            coinString = "{:<5} | {:<10} ({:<5}) | {:<15}".format(
                symbol,
                "$" + quoteData["currentPrice"],
                change24,
                quoteData["name"].title(),
            )
            stringList.append(coinString)
        return "\n".join(stringList)
    else:
        return "Watchlist is empty"


class DuplicateSymbolException(Exception):
    pass


def getCoinDataBySymbol(symbol, botID):
    r = getRedisClient()
    symbolData = None
    if r.hexists(botID, symbol):
        symbolData = json.loads(r.hget(botID, symbol))
    else:
        cmc = CoinMarketCapAPI(os.getenv("CMC_API_KEY"))
        try:
            resp = cmc.cryptocurrency_map(symbol=symbol)
        except CoinMarketCapAPIError as e:
            logging.warning(f"Error finding info for {symbol} with CMC. {e}")
            return f"Unable to find stats for {symbol}"

        cryptoMap = resp.data
        if len(cryptoMap) > 1:
            # Create options, save to dict for future answer, create question to send to group
            options = []
            for num, c in enumerate(cryptoMap, start=1):
                coinData = {
                    "symbol": c["symbol"],
                    "name": c["name"],
                    "cmcID": c["id"],
                    "slug": c["slug"],
                }
                options.append(
                    {
                        "optionNum": num,
                        "params": (coinData, botID),
                        "text": f"{num}. {c['symbol']} | {c['name']}",
                    }
                )
            questionText = "There are more than coins with that symbol. Which should be the default?"
            question = {
                "text": questionText,
                "options": options,
                "callback": "addDefaultToRedis",
            }
            raise DuplicateSymbolException(question)
        elif len(cryptoMap) == 1:
            crypto = cryptoMap[0]
            symbolData = {
                "symbol": crypto["symbol"],
                "name": crypto["name"],
                "cmcID": crypto["id"],
                "slug": crypto["slug"],
            }
            logging.info(f"Got data for {symbol}.\n {symbolData}")
            symbolString = json.dumps(symbolData)
            logging.info(f"Adding {symbol} to redis. {symbolString}")
            r.hset(botID, symbol, symbolString)

    return symbolData


def addDefaultToRedis(coinData, botID):
    coinDataString = json.dumps(coinData)
    logging.info(f"Adding {coinData['symbol']} to redis. {coinDataString}")
    r = getRedisClient()
    r.hset(botID, coinData["symbol"].upper(), coinDataString)


def removeDefault(symbol, botID):
    r = getRedisClient()
    if r.hexists(botID, symbol):
        logging.info(f"Removing default for {symbol}")
        r.hdel(botID, symbol)
        return f"Removed default setting for {symbol}."
    return f"No default found for {symbol}"


def findCoin(argList, botID, defaultSymbol=None):
    if len(argList) == 0 or argList[0] == "":
        symbol = defaultSymbol
    else:
        symbol = argList[0].upper()

    symbolInfo = None
    if symbol:
        symbolInfo = getCoinDataBySymbol(symbol, botID)
    else:
        logging.error(f"No symbol found found for {symbol}.")

    return symbolInfo


def findCryptoInfoCMC(coinData):
    quoteData = getQuoteFromCMC(coinData)
    quote = quoteData["quotes"][coinData["symbol"]]

    returnString = (
        f"{coinData['symbol']} | {coinData['name']}\n"
        f"As of {quoteData['dataDate'].strftime('%I:%M:%S %p')}\n"
        f"Current Price: ${quote['currentPrice']}\n"
        f"Market Cap: ${quote['marketCap']}\n"
        f"Circulating Supply: {quote['circulatingSupply']}\n"
        f"Last Hour: {quote['percent_change_1h']}\n"
        f"Last Day: {quote['percent_change_24h']}\n"
        f"Last Week: {quote['percent_change_7d']}\n"
        f"Last 90 Days: {quote['percent_change_90d']}\n"
    )

    ath = findATH(quote["slug"])

    if ath is not None:
        returnString = returnString + f"ATH: {ath[0]} on {ath[1]}\n"

    logging.debug(f"Expected response for !info")
    logging.debug(returnString)

    return returnString


def findATH(slug):
    try:
        # Get all time high using beautiful soup
        url = BASE_CMC_URL + slug

        req = requests.get(url)

        cryptoPage = bs(req.content, "html5lib")

        athData = cryptoPage.find(text="All Time High")
        athDateStr = athData.parent.nextSibling.text

        athTableRow = athData.parent.parent.parent
        athValues = athTableRow.findAll("span")
        ath = athValues[0].text

        return (ath, athDateStr)
    except Exception:
        logging.warning(f"Failed to get ATH for {slug}.", exc_info=True)


def findPrice(coinData):
    data = getQuoteFromCMC(coinData)

    logging.debug(data)

    return {"date": data["dataDate"].strftime("%I:%M:%S %p"), "quotes": data["quotes"]}


def findPriceString(coinData):
    priceData = findPrice(coinData)
    returnString = f"{coinData['symbol']} | {coinData['name']}\nCurrent Price: ${priceData['quotes'][coinData['symbol']]['currentPrice']}\nAs of {priceData['date']}"

    logging.debug(f"Expected response for !price")
    logging.debug(returnString)

    return returnString


def getPrecisionString(num, precisionOverride=-1, precisionCap=10):
    if type(num) is not str:
        num = str(num)

    pricePrecision = precisionOverride
    # Find the decimals returned
    if len(num.split(".")) > 1 and not precisionOverride > -1:
        pricePrecision = len(num.split(".")[1])
        if len(num.split(".")[0]) >= 3:
            pricePrecision = 2
    # Since we are doing money we want to ensure we have at least 2 decimal points of precision
    if pricePrecision < 2 and not precisionOverride > -1:
        pricePrecision = 2
    pricePrecision = min(precisionCap, pricePrecision)
    productPrice = float(num)
    # Convert number from 1234561.11 to 1,234,561.11
    return f"{productPrice:,.{pricePrecision}f}"


def getPercentString(num):
    if type(num) is not float:
        num = float(num)

    if num >= 100:
        # Put n car emojis dending on how many 100s of percent the value has gone up
        numLambos = math.trunc(num / 100)
        if numLambos > 50:
            lambos = "🚗" * 50
            numLambos = numLambos - 50
            lambos = lambos + f" + {getPrecisionString(str(numLambos), 0)}"
        else:
            lambos = "🚗" * numLambos
        return "+" + getPrecisionString(str(num), 2) + "% Where Lambo? " + lambos
    elif num > 0:
        return "+" + getPrecisionString(str(num), 2) + "% TO THE MOON 🚀🌕"
    else:
        return getPrecisionString(str(num), 2) + "%"


def getQuoteFromCMC(coins):
    if type(coins) is not list:
        coinIDs = [str(coins["cmcID"])]
        coinSymbols = [coins["symbol"]]
        coinList = [coins]
    else:
        coinIDs = [str(c["cmcID"]) for c in coins]
        coinSymbols = [c["symbol"] for c in coins]
        coinList = coins
    logging.debug(f"Getting info for {', '.join(coinSymbols)}")

    cmc = CoinMarketCapAPI(os.getenv("CMC_API_KEY"))

    try:
        print("coinIDs", ",".join(coinIDs))
        resp = cmc.cryptocurrency_quotes_latest(id=",".join(coinIDs))
    except CoinMarketCapAPIError:
        logging.warning(
            f"Error finding info for {', '.join(coinSymbols)} with CMC.", exc_info=True
        )
        return f"Unable to get quote from CoinMarketCap"

    quoteData = None
    for coin in coinList:
        cryptoData = resp.data[str(coin["cmcID"])]

        logging.debug("Crypto Data")
        logging.debug(cryptoData)

        quote = cryptoData["quote"]["USD"]

        logging.debug("Crypto Quote")
        logging.debug(quote)

        if quoteData is None:
            dataDate = (
                datetime.strptime(quote["last_updated"], "%Y-%m-%dT%H:%M:%S.%fZ")
                .replace(tzinfo=pytz.utc)
                .astimezone(pytz.timezone("US/Central"))
            )
            quoteData = {"dataDate": dataDate, "quotes": {}}

        currentPrice = getPrecisionString(quote["price"])
        marketCap = getPrecisionString(quote["market_cap"], 2)
        circulatingSupply = getPrecisionString(cryptoData["circulating_supply"], 0)
        percent_change_1h = getPercentString(quote["percent_change_1h"])
        percent_change_24h = getPercentString(quote["percent_change_24h"])
        percent_change_7d = getPercentString(quote["percent_change_7d"])
        percent_change_90d = getPercentString(quote["percent_change_90d"])

        quoteData["quotes"][coin["symbol"]] = {
            "currentPrice": currentPrice,
            "marketCap": marketCap,
            "circulatingSupply": circulatingSupply,
            "percent_change_1h": percent_change_1h,
            "percent_change_24h": percent_change_24h,
            "percent_change_7d": percent_change_7d,
            "percent_change_90d": percent_change_90d,
            "slug": cryptoData["slug"],
            "name": coin["name"],
        }

    logging.debug(f"Got data object {quoteData}")
    return quoteData


def getSpreadsheetLink(botID):
    r = getRedisClient()
    if r.hexists(botID, "spreadsheet"):
        return r.hget(botID, "spreadsheet")
    else:
        return None
