import asyncio
import aiohttp
import pandas as pd
import requests
from datetime import datetime
import emoji
import telepot
import time
async def get_Pair():
    url = "https://api.coindcx.com/exchange/v1/derivatives/futures/data/active_instruments"
    response = await asyncio.to_thread(requests.get, url)
    data = response.json()
    return data[0:3]

async def get_coindcx_data(pair):
    url = "https://public.coindcx.com/market_data/candlesticks"
    query_params = {
        "pair": str(pair),
        "from": (pd.Timestamp.now() - pd.Timedelta(hours=19, minutes=0)).timestamp(),
        "to": (pd.Timestamp.now() + pd.Timedelta(hours=0, minutes=15)).timestamp(),
        "resolution": "60",  # '1' OR '5' OR '60' OR '1D'
        "pcode": "f"
    }
    response = await asyncio.to_thread(requests.get, url, params=query_params)

    if response.status_code == 200:
        data = response.json()
        data = pd.DataFrame(data['data'])
        #print(data)
        if data.empty is False:
            data['open'] = pd.to_numeric(data['open'])
            data['close'] = pd.to_numeric(data['close'])
            data['high'] = pd.to_numeric(data['high'])
            data['low'] = pd.to_numeric(data['low'])

            # Convert 1-hour candles to 4-hour candles
            data_4h = []
            for i in range(0, len(data), 4):
                block = data.iloc[i:(i+4)+1]
                o = block['open'].iloc[0]
                h = block['high'].max()
                l = block['low'].min()
                c = block['close'].iloc[-1]
                data_4h.append([o, h, l, c])

            data_4h = pd.DataFrame(data_4h, columns=['open', 'high', 'low', 'close'])
            data=data_4h
            #print(data_4h)
            if len(data)>3:
              # Check for your specific pattern
              if data['low'][0] < data['low'] [1]< data['low'][2] and data['close'][0] < data['close'][1] < data[
                'close'][2]:
                 return pair
            else:pass

async def update_data_for_coins(coin_list):
    tasks = [get_coindcx_data(coin) for coin in coin_list]
    results = await asyncio.gather(*tasks)
    #print(coin_list)
    for result in results:
        if result:
            print(result)


async def main():
    while True:
        current_minute = datetime.now().minute
        current_second = datetime.now().second
        print(f"{current_minute:02d}:{current_second:02d}", end='\r', flush=True)
        if current_minute % 1 == 0:
            time.sleep(5)
            coins_to_track = await get_Pair()
            await update_data_for_coins(coins_to_track)
            print("///////////////////////////")
            await asyncio.sleep(60)  # Sleep for 60 seconds


asyncio.run(main())