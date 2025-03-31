import asyncio
import aiohttp
import pandas as pd
import requests
from datetime import datetime
import emoji
import telepot
import time
green_heart = emoji.emojize(":green_heart:")
red_heart = emoji.emojize(":red_heart:")
bot = telepot.Bot('5925692200:AAGiOqrvaAKAZOx0SW__Ypst6--kG62zUes')
chatid='-1001837443634'
purl = "https://api.coindcx.com/exchange/v1/derivatives/futures/data/active_instruments"
response = requests.get(purl)
data = response.json()
pairs = list(data)

msgs=""
def send_signal_message(symbol, signal_value, side, heart):
    message = f"{symbol} with signal value: {signal_value:.2f}% {side}{heart}"
    msgs.append((abs(signal_value), message))



async def fetch_candlestick(pair, session):
            url = "https://public.coindcx.com/market_data/candlesticks"
            query_params = {
                "pair": str(pair),
                "from": (pd.Timestamp.now() - pd.Timedelta(hours=19)).timestamp(),
                "to": (pd.Timestamp.now() + pd.Timedelta(hours=0, minutes=15)).timestamp(),
                "resolution": "60",  # '1' OR '5' OR '60' OR '1D'
                "pcode": "f"
            }
            async with session.get(url, params=query_params) as response:
                if response.status == 200:
                    data = await response.json()
                    data = pd.DataFrame(data['data'])
                    #print(current_hour)
                    if ((current_hour) + 3) % 4 == 0:
                        data = data[8:12]
                        #print(data)
                    elif (current_hour + 2) % 4 == 0:
                        data = data[7:11]
                        #print(data)
                    elif (current_hour + 1) % 4 == 0:
                        data = data[6:10]
                        #print(data)
                    if data.empty is False:
                        data['open'] = pd.to_numeric(data['open'])
                        data['close'] = pd.to_numeric(data['close'])
                        data['high'] = pd.to_numeric(data['high'])
                        data['low'] = pd.to_numeric(data['low'])

                        # Convert 1-hour candles to 4-hour candles
                        data_4h = []
                        for i in range(0, len(data), 4):
                            block = data.iloc[i:(i + 4) + 1]
                            o = block['open'].iloc[0]
                            h = block['high'].max()
                            l = block['low'].min()
                            c = block['close'].iloc[-1]
                            data_4h.append([o, h, l, c])

                        data_4h = pd.DataFrame(data_4h, columns=['open', 'high', 'low', 'close'])
                        data = data_4h
                        data['signal'] = ((data['close'] - data['open']) / data['open']) * 100
                        #print(pair,data)
                        if data['signal'][0] > 1.0:
                            send_signal_message(pair, data['signal'][0], green_heart, "LONG")
                        elif data['signal'][0] < -1.0:
                            send_signal_message(pair, data['signal'][0], red_heart, "SHORT")

                else:
                    print(f"Error fetching data for {pair}: {response.status}")

        # Wait for 1 minute before checking again



async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_candlestick(pair, session) for pair in pairs]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    while True:
       current_minute = datetime.now().minute
       current_second = datetime.now().second
       current_hour=datetime.now().hour

       print(f"{current_minute:02d}:{current_second:02d}", end='\r', flush=True)
       if current_minute%1==0:
           msgs = []
           asyncio.run(main())
           msgs.sort(reverse=True)
           message = "\n".join([msg[1] for msg in msgs])
           print(message,'\n')
           time.sleep(60)


