import os
import pytz
import math

from datetime import datetime

from Utils.loggerUtils import LOGGER

from coinmarketcapapi import CoinMarketCapAPI, CoinMarketCapAPIError
from bs4 import BeautifulSoup as bs
import requests

BASE_CMC_URL = 'https://coinmarketcap.com/currencies/'


def findCryptoInfoCMC(argList):
    if len(argList) == 0 or argList[0] == '':
        symbol = 'SHIB'
    else:
        symbol = argList[0].upper()

    quote = getQuoteFromCMC(symbol)

    try:
        # Get all time high using beautiful
        url = BASE_CMC_URL + quote['slug']

        req = requests.get(url)

        cryptoPage = bs(req.content, 'html5lib')

        athData = cryptoPage.find(text='All Time High')
        athDateStr = athData.parent.nextSibling.text

        athTableRow = athData.parent.parent.parent
        athValues = athTableRow.findAll('span')
        ath = athValues[0].text
        # Get the percent down. Need better way to display before adding
        # athPercent = athValues[1].text
        # if athTableRow.find("span", {"class": "icon-Caret-down"}):
        #     athPercent = athPercent + '📉'
        # else:
        #     athPercent = athPercent + '📈'
    except Exception as e:
        LOGGER.warn(f"Failed to get ATH for {symbol}. {e}")
        returnString = (
            f"Price Information for {symbol} as of {quote['dataDate']}\n"
            f"Current Price: ${quote['currentPrice']}\n"
            f"Market Cap: ${quote['marketCap']}\n"
            f"Circulating Supply: {quote['circulatingSupply']}\n"
            f"Last Hour: {quote['percent_change_1h']}\n"
            f"Last Day: {quote['percent_change_24h']}\n"
            f"Last Week: {quote['percent_change_7d']}\n"
            f"Last 90 Days: {quote['percent_change_90d']}\n"
        )
    else:
        returnString = (
            f"Price Information for {symbol} as of {quote['dataDate']}\n"
            f"Current Price: ${quote['currentPrice']}\n"
            f"ATH: {ath} on {athDateStr}\n"
            f"Market Cap: ${quote['marketCap']}\n"
            f"Circulating Supply: {quote['circulatingSupply']}\n"
            f"Last Hour: {quote['percent_change_1h']}\n"
            f"Last Day: {quote['percent_change_24h']}\n"
            f"Last Week: {quote['percent_change_7d']}\n"
            f"Last 90 Days: {quote['percent_change_90d']}\n"
        )

    LOGGER.debug(f'Expected response for !info')
    LOGGER.debug(returnString)

    return returnString


def getPrecisionString(num, precisionOverride=-1, precisionCap=10):
    if type(num) is not str:
        num = str(num)

    pricePrecision = precisionOverride
    # Find the decimals returned
    if len(num.split('.')) > 1 and not precisionOverride > -1:
        pricePrecision = len(num.split('.')[1])
    # Since we are doing money we want to ensure we have at least 2 decimal points of precision
    if pricePrecision < 2 and not precisionOverride > -1:
        pricePrecision = 2
    pricePrecision = min(precisionCap, pricePrecision)
    productPrice = float(num)
    # Convert number from 1234561.11 to 1,234,561.11
    return f'{productPrice:,.{pricePrecision}f}'


def getPercentString(num):
    if type(num) is not float:
        num = float(num)

    if num >= 100:
        # Put n car emojis dending on how many 100s of percent the value has gone up
        numLambos = math.trunc(num / 100)
        if numLambos > 50:
            lambos = '🚗' * 50
            numLambos = numLambos - 50
            lambos = lambos + f' + {getPrecisionString(str(numLambos), 0)}'
        else:
            lambos = '🚗' * numLambos
        return '+' + getPrecisionString(str(num), 2) + '% Where Lambo? ' + lambos
    elif num > 0:
        return '+' + getPrecisionString(str(num), 2) + '% TO THE MOON 🚀🌕'
    else:
        return getPrecisionString(str(num), 2) + '%'


def findPrice(argList):
    if len(argList) == 0 or argList[0] == '':
        symbol = 'SHIB'
    else:
        symbol = argList[0].upper()

    quote = getQuoteFromCMC(symbol)

    returnString = f"Current price of {symbol} at {quote['dataDate']} is ${quote['currentPrice']}."

    LOGGER.debug(f'Expected response for !price')
    LOGGER.debug(returnString)

    return returnString


def getQuoteFromCMC(symbol):
    LOGGER.debug(f"Getting info for {symbol}")

    cmc = CoinMarketCapAPI(os.getenv('CMC_API_KEY'))

    resp = cmc.cryptocurrency_quotes_latest(symbol=symbol)

    if not resp.ok:
        LOGGER.warn(f"Error finding info for {symbol} with CMC. {resp.status}")
        return f'Unable to find stats for {symbol}'

    cryptoData = resp.data[symbol]

    LOGGER.debug("Crypto Data")
    LOGGER.debug(cryptoData)

    quote = cryptoData['quote']['USD']

    LOGGER.debug("Crypto Quote")
    LOGGER.debug(quote)

    dataDate = datetime.strptime(quote['last_updated'], '%Y-%m-%dT%H:%M:%S.%fZ') \
        .replace(tzinfo=pytz.utc) \
        .astimezone(pytz.timezone('US/Central')) \
        .strftime("%I:%M:%S %p")
    currentPrice = getPrecisionString(quote['price'])
    marketCap = getPrecisionString(quote['market_cap'], 2)
    circulatingSupply = getPrecisionString(cryptoData['circulating_supply'], 0)
    percent_change_1h = getPercentString(quote['percent_change_1h'])
    percent_change_24h = getPercentString(quote['percent_change_24h'])
    percent_change_7d = getPercentString(quote['percent_change_7d'])
    percent_change_90d = getPercentString(quote['percent_change_90d'])

    returnQuote = {
        'dataDate': dataDate,
        'currentPrice': currentPrice,
        'marketCap': marketCap,
        'circulatingSupply': circulatingSupply,
        'percent_change_1h': percent_change_1h,
        'percent_change_24h': percent_change_24h,
        'percent_change_7d': percent_change_7d,
        'percent_change_90d': percent_change_90d,
        'slug': cryptoData['slug']
    }

    LOGGER.debug(f'Got data object {returnQuote}')
    return returnQuote


'''
USE BE4 test

Current price: shibPage.find('div', 'priceValue').text

'''
