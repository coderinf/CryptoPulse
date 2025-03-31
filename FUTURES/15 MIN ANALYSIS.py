import emoji
import requests
import pandas as pd
import telepot
import time
from datetime import datetime
bot = telepot.Bot('5925692200:AAGiOqrvaAKAZOx0SW__Ypst6--kG62zUes')
chatid='-1001837443634'
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
 "from": (pd.Timestamp.now()-pd.Timedelta(hours=6)).timestamp(),
 "to": (pd.Timestamp.now()+pd.Timedelta(hours=0,minutes=15)).timestamp(),
 "resolution": "15", # '1' OR '5' OR '60' OR '1D'
 "pcode": "f"
 }
 response = requests.get(url, params=query_params)

 if response.status_code == 200:
  data = response.json()
  data=pd.DataFrame(data['data'])
  if data.empty is False:
    data['open'] = pd.to_numeric(data['open'])
    data['close'] = pd.to_numeric(data['close'])

  # Add the 'signal' column
    data['signal'] = ((data['close'] - data['open']) / data['open']) * 100

  # Process the data as needed
    return data
  elif data.empty is True:
      return []
  else:
   return (f"Error: {response.status_code}, {response.text}")


def send_signal_message(symbol, signal_value, side,heart):
 message = f"{symbol} with signal value: {signal_value:.2f}% {side}{heart}"
 # Replace the following line with your actual implementation for sending messages
 bot.sendMessage(chatid, message)
 print(message)

def update_data_for_coins(coin_list):
  interval = "5m"  # 15-minute time interval

  for symbol in coin_list:
    data = get_coindcx_data(symbol)
    if type(data) is not list:
     signal_value = data['signal'].iloc[-2]  # Extract the signal value from the last row

     if signal_value > 1.0:
      send_signal_message(symbol, signal_value,green_heart, "LONG")
     elif signal_value < -1.0:
      send_signal_message(symbol, signal_value,red_heart, "SHORT")

coins_to_track =get_Pair()

while True:
    current_minute = datetime.now().minute
    current_second = datetime.now().second
    print(f"{current_minute:02d}:{current_second:02d}", end='\r', flush=True)

    if current_minute % 1== 0:
        bot.sendMessage(chatid,"///////////////////////////////////////////////////////////////")
        bot.sendMessage(chatid,f"Signals detected {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        time.sleep(1)
        update_data_for_coins(coins_to_track)
        print("///////////////////////////")
        time.sleep(60)  # Sleep for 900 seconds (15 minutes)
