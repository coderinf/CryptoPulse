import socketio
import hmac
import hashlib
import json
import time
import asyncio
from datetime import datetime
import requests



from socketio.exceptions import TimeoutError
socketEndpoint = 'wss://stream.coindcx.com'
sio = socketio.AsyncClient()

key="44ed7979643b133d4bf23ecd145c8d30cccbee6b829a4f8d"

secret="69b9938908fab3a9965891d8d318e5db2ae8105f2d518a801273cbdf7ad4f552"


# python3
secret_bytes = bytes(secret, encoding='utf-8')
channelName = "coindcx"
body = {"channel": channelName}
json_body = json.dumps(body, separators=(',', ':'))
signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()


async def ping_task():
    while True:
        await asyncio.sleep(25)
        try:
            await sio.emit('ping', {'data': 'Ping message'})
        except Exception as e:
            print(f"Error sending ping: {e}")


@sio.event
async def connect():
    print("I'm connected!")
    current_time = datetime.now()
    print("Connected Time:", current_time.strftime("%Y-%m-%d %H:%M:%S"))

    await sio.emit('join', {'channelName': "coindcx", 'authSignature': signature, 'apiKey': key})
    await sio.emit('join', {'channelName': "B-DOGE_USDT@prices-futures"})


@sio.on('price-change')
async def on_message(response):
    current_time = datetime.now()
    data=response['data']
    data=json.loads(data)
    capture(data['p'])
# client requirements goes here
def create_order(coin,price):
# python3
   secret_bytes = bytes(secret, encoding='utf-8')
   # Generating a timestamp
   timeStamp = int(round(time.time() * 1000))
   body = {
   "timestamp":timeStamp , # EPOCH timestamp in seconds
   "order": {
   "side": "buy", # buy OR sell
   "pair": str(coin), # instrument.string
   "order_type": "limit_order", # market_order OR limit_order
   "price": str(price), #numeric value
   "total_quantity": 50, #numerice value
   "leverage": 4, #numerice value
   "notification": "email_notification", # no_notification OR
   "time_in_force": "good_till_cancel", # good_till_cancel OR
   "hidden": False, # True or False
   "post_only": False # True or False
   }
   }
   json_body = json.dumps(body, separators = (',', ':'))
   signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()
   url = "https://api.coindcx.com/exchange/v1/derivatives/futures/orders/create"
   headers = {
   'Content-Type': 'application/json',
   'X-AUTH-APIKEY': key,
   'X-AUTH-SIGNATURE': signature
   }
   response = requests.post(url, data = json_body, headers = headers)
   data = response.json()
   print(data)

def capture(price):
    print("price change is "+price)
    if float(price)<0.21700:
     create_order('B-DOGE_USDT',0.21700)

async def main():
    try:
        await sio.connect(socketEndpoint, transports='websocket')
        # Wait for the connection to be established
        asyncio.create_task(ping_task())

        await sio.wait()
        while True:
            time.sleep(1)
            sio.event('price-change', {'channelName': "B-DOGE_USDT@prices-futures"})
            capture(sio.event('price-change', {'channelName': "B-DOGE_USDT@prices-futures"}))
    except Exception as e:
        print(f"Error connecting to the server: {e}")
        raise  # re-raise the exception to see the full traceback


asyncio.run(main())
         