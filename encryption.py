import secrets
from Crypto.Cipher import AES
import hashlib
from Crypto import Random
import os
import uuid
import base64


class AESCipher(object):

    def __init__(self, key): 
        self.bs = AES.block_size
        self.key = key #256 bit for AES-256 with PKCS#7 padding

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw.encode())).decode()

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