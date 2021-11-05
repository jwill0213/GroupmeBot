import os
import pytz
import math

from datetime import datetime
from nomics import Nomics

from Utils.loggerUtils import LOGGER


def findCryptoInfo(argList):
    if len(argList) == 0:
        symbol = 'SHIB'
    else:
        symbol = argList[0].upper()

    LOGGER.debug(f"Getting info for {symbol}")

    nomics = Nomics(os.getenv('NOMICS_API_KEY'))

    priceList = nomics.Currencies.get_currencies(
        ids=symbol, interval='1h,1d,7d,365d')

    LOGGER.debug("Price List")
    LOGGER.debug(priceList)

    if len(priceList) == 1:
        symbolData = priceList[0]
    else:
        return f"Price information not found for {symbol}"

    dataDate = datetime.strptime(symbolData['price_timestamp'], '%Y-%m-%dT%H:%M:%SZ') \
        .replace(tzinfo=pytz.utc) \
        .astimezone(pytz.timezone('US/Central')) \
        .strftime("%I:%M:%S %p")
    athDate = datetime.strptime(symbolData['high_timestamp'], '%Y-%m-%dT%H:%M:%SZ') \
        .replace(tzinfo=pytz.utc) \
        .astimezone(pytz.timezone('US/Central')) \
        .strftime("%Y-%m-%d")
    currentPrice = getPrecisionString(symbolData['price'])
    ath = getPrecisionString(symbolData['high'])
    marketCap = getPrecisionString(symbolData['market_cap'], 0)
    circulatingSupply = getPrecisionString(symbolData['circulating_supply'], 0)
    hourChange = getPercentString(
        float(symbolData['1h']['price_change_pct'])*100)
    dayChange = getPercentString(
        float(symbolData['1d']['price_change_pct'])*100)
    weekChange = getPercentString(
        float(symbolData['7d']['price_change_pct'])*100)
    yearChange = getPercentString(
        float(symbolData['365d']['price_change_pct'])*100)

    returnString = (
        f"Price Information for {symbol} as of {dataDate}\n"
        f"Current Price: ${currentPrice}\n"
        f"ATH: ${ath} on {athDate}\n"
        f"Market Cap: ${marketCap}\n"
        f"Circulating Supply: {circulatingSupply}\n"
        f"Last Hour: {hourChange}\n"
        f"Last Day: {dayChange}\n"
        f"Last Week: {weekChange}\n"
        f"Last Year: {yearChange}\n"
    )

    LOGGER.debug(f'Expected response for !info')
    LOGGER.debug(returnString)

    return returnString


def getPrecisionString(num, precisionOverride=-1):
    pricePrecision = precisionOverride
    # Find the decimals returned
    if len(num.split('.')) > 1 and not precisionOverride > -1:
        pricePrecision = len(num.split('.')[1])
    # Since we are doing money we want to ensure we have at least 2 decimal points of precision
    if pricePrecision < 2 and not precisionOverride > -1:
        pricePrecision = 2
    productPrice = float(num)
    # Convert number from 1234561.11 to 1,234,561.11
    return f'{productPrice:,.{pricePrecision}f}'


def getPercentString(num):
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
    if len(argList) == 0:
        symbol = 'SHIB'
    else:
        symbol = argList[0].upper()

    nomics = Nomics(os.getenv('NOMICS_API_KEY'))

    priceList = nomics.Currencies.get_currencies(
        ids=symbol, interval='1h,1d,7d')

    if len(priceList) == 1:
        symbolData = priceList[0]
    else:
        return f"Price information not found for {symbol}"

    currentPrice = getPrecisionString(symbolData['price'])
    dataDate = datetime.strptime(symbolData['price_timestamp'], '%Y-%m-%dT%H:%M:%SZ') \
        .replace(tzinfo=pytz.utc) \
        .astimezone(pytz.timezone('US/Central')) \
        .strftime("%I:%M:%S %p")

    LOGGER.debug(f'Expected response for !info')
    LOGGER.debug(
        f"Current price of {symbol} at {dataDate} is ${currentPrice}.")

    return f"Current price of {symbol} at {dataDate} is ${currentPrice}."


'''
USE BE4 test

Current price: shibPage.find('div', 'priceValue').text

'''
