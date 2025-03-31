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
    await sio.emit('join', {'channelName': "B-CKB_USDT@prices-futures"})


@sio.on('price-change')
async def on_message(response):
    current_time = datetime.now()
    data=response['data']
    data=json.loads(data)
    capture(data['p'])
# client requirments goes here
def capture(price):
    print("price change is "+price)
async def main():
    try:
        await sio.connect(socketEndpoint, transports='websocket')
        # Wait for the connection to be established
        asyncio.create_task(ping_task())

        await sio.wait()
        while True:
            time.sleep(1)
            #sio.event('price-change', {'channelName': "B-DOGE_USDT@prices-futures"})
           # capture(sio.event('price-change', {'channelName': "B-W_USDT@prices-futures"}))
    except Exception as e:
        print(f"Error connecting to the server: {e}")
        raise  # re-raise the exception to see the full traceback


asyncio.run(main())
