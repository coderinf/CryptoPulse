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
chatid = '-1001837443634'

purl = "https://api.coindcx.com/exchange/v1/derivatives/futures/data/active_instruments"
response = requests.get(purl)
data = response.json()
pairs = list(data)

msgs = []

def send_signal_message(symbol, signal_value, side, heart):
    message = f"{symbol} with signal value: {signal_value:.2f}% {side}{heart}"
    msgs.append((abs(signal_value), message))

async def fetch_candlestick(pair, session):
    max_retries = 3
    retries = 0
    while retries < max_retries:
        try:
            url = "https://public.coindcx.com/market_data/candlesticks"
            query_params = {
                "pair": str(pair),
                "from": (pd.Timestamp.now() - pd.Timedelta(hours=6)).timestamp(),
                "to": (pd.Timestamp.now() + pd.Timedelta(hours=0, minutes=5)).timestamp(),
                "resolution": "5",  # '1' OR '5' OR '60' OR '1D'
                "pcode": "f"
            }
            async with session.get(url, params=query_params) as response:
                if response.status == 200:
                    data = await response.json()
                    data = pd.DataFrame(data['data'])
                    if not data.empty:
                        data['open'] = pd.to_numeric(data['open'])
                        data['close'] = pd.to_numeric(data['close'])
                        data['signal'] = ((data['close'] - data['open']) / data['open']) * 100
                        a = 4
                        if data['signal'][a] > 1.0:
                            send_signal_message(pair, data['signal'][a], green_heart, "LONG")
                        elif data['signal'][a] < -1.0:
                            send_signal_message(pair, data['signal'][a], red_heart, "SHORT")
                else:
                    print(f"Error fetching data for {pair}: {response.status}")
            break
        except aiohttp.client_exceptions.ServerDisconnectedError:
            retries += 1
            await asyncio.sleep(1)  # Wait for 1 second before retrying
    else:
        raise Exception("Failed to fetch candlestick data after {} retries".format(max_retries))

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_candlestick(pair, session) for pair in pairs]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    while True:
        current_minute = datetime.now().minute
        current_second = datetime.now().second

        print(f"{current_minute:02d}:{current_second:02d}", end='\r', flush=True)
        if current_minute % 1 == 0:
            msgs = []
            asyncio.run(main())
            msgs.sort(reverse=True)
            message = "\n".join([msg[1] for msg in msgs])
            print(message,"\n")

            if message:
                bot.sendMessage(chatid, message)
            else:
                bot.sendMessage(chatid, "No signals generated this 5 min cycle.")
            time.sleep(60)