# ShAfT: Shell over Api for Twitter

# Overview

This is a multi-client shell That uses Twitter's streaming and REST APIs to send and receive shell states between a client/server, No port forwarding needed, and the server need not be running at all times. Commands are encrypted with AES-256 and packaged as nice QR codes to avoid the classic character limit ;). feel free to contribute just for the banter, but as you can probably tell, this is by no means a realistic prospect because of the overhead, it was merely a fun project to get to know Twitter's API.


# How to Use

To use this shell, two scripts need to be running

* **server.py** - runs on anything with an internet connection + python and waits for clients to connect
* **client.py** - connects to twitter and is recognised by the server - also runs on anything with an internet connection + python
***
## API Keys and Twitter User ID
In order to use either the client or server, you need to [make a twitter app and get your keys](https://developer.twitter.com/) (this is assuming you already have a twitter account lol).

Once you have your keys, create a python file in the same directory as both `client.py` and `server.py` (you need keys for both, can be the same app keys) called `api_keys.py`. In your `api_keys.py` file, initialise a dictionary with the following key:value pairs like so:

```
api_keys = {}
api_keys['consumer_key'] = 'YOUR_CONSUMER_KEY'
api_keys['consumer_secret'] = 'YOUR_CONSUMER_SECRET'
api_keys['access_token'] = 'YOUR_ACCESS_TOKEN'
api_keys['access_token_secret'] = 'YOUR_ACCESS_TOKEN_SECRET'
api_keys['my_user_id'] = 'YOUR TWITTER USER ID'
```
Then you should be good to go assuming you have all the requrements installed!

## Server

To set up the server script, simply run **server.py** using Python 3.4+

`python3 server.py`

You will then enter an interactive prompt where you are able to view connected clients available to that server as saved in the newly generated `clients.db`, select a specific client by entering their hex value from the list, and send commands to that client remotely over twitter!

To list all current clients or exit ShAfT:

`exit ShAfT`

this will close the current client's connection and allow you to select another client or exit the server.
***

## Client

For **client.py**, simply run the python script!
