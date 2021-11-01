from datetime import datetime, timedelta
import cbpro
import pytz


def run(data, bot_info, send):
    message = data['text']

    if message == '!price':
        productId = 'SHIB-USD'
        client = cbpro.PublicClient()
        shib = client.get_product_ticker(productId)
        dateString = datetime.strptime(shib['time'], '%Y-%m-%dT%H:%M:%S.%fZ') \
            .replace(tzinfo=pytz.utc) \
            .astimezone(pytz.timezone('US/Central')) \
            .strftime("%I:%M:%S %p")
        priceString = f"Current price of {productId} at {dateString} is ${shib['price']}. {data}"
        send(priceString, bot_info[0])
        return True

    if message == '!test':
        send(
            "Hi there! Your bot is working, you should start customizing it now.", bot_info[0])
        return True

    return True

# start = dt.now() - td(hours=3)
# hist = client.get_product_historic_rates('SHIB-USD', granularity=60, start=start.astimezone(CST).isoformat(), end=dt.now().astimezone(CST).isoformat())
# for x in hist:
#     print(dt.fromtimestamp(x[0]).astimezone(CST).strftime('%Y/%m/%d %I:%M:%S %p'), "${:.7f}". format(x[1]))
