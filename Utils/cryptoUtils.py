from datetime import datetime
import os
import pytz
from Utils.loggerUtils import LOGGER

from nomics import Nomics


def findCryptoInfo(argList):
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

    dataDate = datetime.strptime(symbolData['price_timestamp'], '%Y-%m-%dT%H:%M:%SZ') \
        .replace(tzinfo=pytz.utc) \
        .astimezone(pytz.timezone('US/Central')) \
        .strftime("%I:%M:%S %p")
    currentPrice = getPrecisionString(symbolData['price'])
    marketCap = getPrecisionString(symbolData['market_cap'], 0)
    circulatingSupply = getPrecisionString(symbolData['circulating_supply'], 0)
    hourChange = getPercentString(
        float(symbolData['1h']['price_change_pct'])*100)
    dayChange = getPercentString(
        float(symbolData['1d']['price_change_pct'])*100)
    weekChange = getPercentString(
        float(symbolData['7d']['price_change_pct'])*100)

    returnString = (
        f"Price Information for {symbol} as of {dataDate}\n"
        f"Current Price: ${currentPrice}\n"
        f"Market Cap: ${marketCap}\n"
        f"Circulating Supply: {circulatingSupply}\n"
        f"Change Last Hour: {hourChange}\n"
        f"Change Last Day: {dayChange}\n"
        f"Change Last Week: {weekChange}\n"
    )

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
    if num > 0:
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

    return f"Current price of {symbol} at {dataDate} is ${currentPrice}."
