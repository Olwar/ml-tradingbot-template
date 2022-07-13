import json, hmac, hashlib, time, requests, base64
from requests.auth import AuthBase
import urllib

# Kraken API info
api_url = "https://api.KRAKEN.com"
api_key = "YOUR KRAKEN API KEY"
api_sec = "YOUR KRAKEN API SECRET KEY"

# Telegram bot to send you updates on the trades
def telegram_bot_sendtext(bot_message): 
    bot_token = 'YOUR BOT TOKEN'
    bot_chatID = 'YOUR CHAT ID'
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message

    response = requests.get(send_text)

# Authorizing Kraken API
def get_kraken_signature(urlpath, data, secret):

    postdata = urllib.parse.urlencode(data)
    encoded = (str(data['nonce']) + postdata).encode()
    message = urlpath.encode() + hashlib.sha256(encoded).digest()

    mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
    sigdigest = base64.b64encode(mac.digest())
    return sigdigest.decode()

# Setuppin Kraken API
def kraken_request(uri_path, data, api_key, api_sec):
    headers = {}
    headers['API-Key'] = api_key
    # get_kraken_signature() as defined in the 'Authentication' section
    headers['API-Sign'] = get_kraken_signature(uri_path, data, api_sec)             
    req = requests.post((api_url + uri_path), headers=headers, data=data)
    return req
