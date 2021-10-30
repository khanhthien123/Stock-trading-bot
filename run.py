import trade
from datetime import datetime, time, date

now = datetime.now().time()
time_0630am = time(6, 30, 00)
time_1230pm = time(12, 30, 00)

trade.load_data()

while now > time_0630am and now < time_1230pm:
    print("---- Market is open ------")
    trade.shouldSell()
    trade.shouldBuy()

print("Market closed")