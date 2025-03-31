import emoji
import requests
import pandas as pd
import telepot
import time
from datetime import datetime

bot = telepot.Bot('5925692200:AAGiOqrvaAKAZOx0SW__Ypst6--kG62zUes')
chatid = '-1001837443634'
green_heart = emoji.emojize(":green_heart:")
red_heart = emoji.emojize(":red_heart:")


def get_Pair():
    url = "https://api.coindcx.com/exchange/v1/derivatives/futures/data/active_instruments"
    response = requests.get(url)
    data = response.json()
    return data


def get_coindcx_data(pair):
    url = "https://public.coindcx.com/market_data/candlesticks"
    query_params = {
        "pair": str(pair),
        "from": (pd.Timestamp.now() - pd.Timedelta(hours=6, minutes=45)).timestamp(),
        "to": (pd.Timestamp.now() + pd.Timedelta(hours=0, minutes=15)).timestamp(),
        "resolution": "15",  # '1' OR '5' OR '60' OR '1D'
        "pcode": "f"
    }
    response = requests.get(url, params=query_params)

    if response.status_code == 200:
        data = response.json()
        data = pd.DataFrame(data['data'])
        if data.empty is False:
            data['open'] = pd.to_numeric(data['open'])
            data['close'] = pd.to_numeric(data['close'])





# def send_signal_message(symbol, signal_value, side,heart):
# message = f"{symbol} with signal value: {signal_value:.2f}% {side}{heart}"
# Replace the following line with your actual implementation for sending messages
# bot.sendMessage(chatid, message)
# print(message)

def update_data_for_coins(coin_list):
    for symbol in coin_list:
        data = get_coindcx_data(symbol)
        if data:
         print(data)

coins_to_track = get_Pair()

while True:
    current_minute = datetime.now().minute
    current_second = datetime.now().second
    print(f"{current_minute:02d}:{current_second:02d}", end='\r', flush=True)
    if current_minute % 15== 0:
        time.sleep(5)
        update_data_for_coins(coins_to_track)
        print("///////////////////////////")
        time.sleep(60)  # Sleep for 900 seconds (15 minutes)
