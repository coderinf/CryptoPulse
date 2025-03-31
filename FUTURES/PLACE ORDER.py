import hmac
import hashlib
import base64
import json
import time
import requests
# Enter your API Key and Secret here. If you don't have one, you can generate

key="44ed7979643b133d4bf23ecd145c8d30cccbee6b829a4f8d"

secret="69b9938908fab3a9965891d8d318e5db2ae8105f2d518a801273cbdf7ad4f552"


# python3
secret_bytes = bytes(secret, encoding='utf-8')
# Generating a timestamp
timeStamp = int(round(time.time() * 1000))
body = {
"timestamp":timeStamp , # EPOCH timestamp in seconds
"order": {
"side": "buy", # buy OR sell
"pair": "B-ID_USDT", # instrument.string
"order_type": "limit_order", # market_order OR limit_order
"price": "0.2962", #numeric value
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
