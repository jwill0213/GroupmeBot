from datetime import datetime, timedelta
import cbpro
import pytz


def run(data, bot_info, send):
    message = data['text']

    cmd, *args = message.split(' ')

    if cmd == '!price':
        if len(args) == 0:
            ticker = 'SHIB'
        else:
            ticker = args[0].upper()
        productId = f'{ticker}-USD'
        client = cbpro.PublicClient()
        product = client.get_product_ticker(productId)
        if 'message' in product:
            send("Requested price was not found.", bot_info[0])
            return True
        dateString = datetime.strptime(product['time'], '%Y-%m-%dT%H:%M:%S.%fZ') \
            .replace(tzinfo=pytz.utc) \
            .astimezone(pytz.timezone('US/Central')) \
            .strftime("%I:%M:%S %p")
        priceString = f"Current price of {productId} at {dateString} is ${product['price']}."
        send(priceString, bot_info[0])
        return True

    return True

# start = dt.now() - td(hours=3)
# hist = client.get_product_historic_rates('SHIB-USD', granularity=60, start=start.astimezone(CST).isoformat(), end=dt.now().astimezone(CST).isoformat())
# for x in hist:
#     print(dt.fromtimestamp(x[0]).astimezone(CST).strftime('%Y/%m/%d %I:%M:%S %p'), "${:.7f}". format(x[1]))
