from datetime import datetime, timedelta
import cbpro
import pytz

CST = pytz.all_timezones

def runBot():
    pass

# start = dt.now() - td(hours=3)
# hist = client.get_product_historic_rates('SHIB-USD', granularity=60, start=start.astimezone(CST).isoformat(), end=dt.now().astimezone(CST).isoformat())
# for x in hist:
#     print(dt.fromtimestamp(x[0]).astimezone(CST).strftime('%Y/%m/%d %I:%M:%S %p'), "${:.7f}". format(x[1]))

if __name__ == '__main__':
    runBot()
