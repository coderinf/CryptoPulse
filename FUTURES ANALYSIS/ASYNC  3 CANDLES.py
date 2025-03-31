import emoji
import requests
import pandas as pd
import telepot
import time
import asyncio
from datetime import datetime

bot = telepot.Bot('5925692200:AAGiOqrvaAKAZOx0SW__Ypst6--kG62zUes')
chatid = '-1001837443634'
green_heart = emoji.emojize(":green_heart:")
red_heart = emoji.emojize(":red_heart:")


async def get_Pair():
    url = "https://api.coindcx.com/exchange/v1/derivatives/futures/data/active_instruments"
    response = await asyncio.to_thread(requests.get, url)
    data = response.json()
    return data


async def get_coindcx_data(pair):
    url = "https://public.coindcx.com/market_data/candlesticks"
    query_params = {
        "pair": str(pair),
        "from": (pd.Timestamp.now() - pd.Timedelta(hours=6, minutes=30)).timestamp(),
        "to": (pd.Timestamp.now() + pd.Timedelta(hours=0, minutes=15)).timestamp(),
        "resolution": "15",  # '1' OR '5' OR '60' OR '1D'
        "pcode": "f"
    }
    response = await asyncio.to_thread(requests.get, url, params=query_params)

    if response.status_code == 200:
        data = response.json()
        data = pd.DataFrame(data['data'])
        #print(pair,data)
        if data.empty is False:
            data['open'] = pd.to_numeric(data['open'])
            data['close'] = pd.to_numeric(data['close'])

            if data['low'][0] < data['low'] [1]< data['low'][2] and data['close'][0] < data['close'][1] < data[
                'close'][2]:
                return pair


async def update_data_for_coins(coin_list):
    tasks = [get_coindcx_data(coin) for coin in coin_list]
    results = await asyncio.gather(*tasks)
    for result in results:
        if result:
            print(result)



async def main():
    while True:
        current_minute = datetime.now().minute
        current_second = datetime.now().second
        print(f"{current_minute:02d}:{current_second:02d}", end='\r', flush=True)
        if current_minute % 15 == 0:
            #time.sleep(5)
            coins_to_track = await get_Pair()
            await update_data_for_coins(coins_to_track)
            print("///////////////////////////")
            await asyncio.sleep(60)  # Sleep for 60 seconds


asyncio.run(main())