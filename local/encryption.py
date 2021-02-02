import socket
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad
from Cryptodome.Random import get_random_bytes
from base64 import b64encode, b64decode
from getpass import getpass
import json

# Class to handle AES encryption and decryption, initialized at start with secret sixteen bit key
class EncryptionHandler():
    key = None

    def __init__(self, key: bytes):
        self.key = key

    def encrypt_msg(self, message):
        cipher = AES.new(self.key, AES.MODE_CBC)
        message += ' ' * (16 - len(message) % 16)
        ct_bytes = cipher.encrypt(message.encode())
        print(AES.block_size)
        iv = cipher.iv
        ct = ct_bytes
        # json_bytes = json.dumps({'iv': iv, 'ciphertext': ct}).encode()
        encryptedMessage = b64encode(cipher.iv + ct_bytes)
        print(encryptedMessage)
        return encryptedMessage

    def decrypt_message(self, cipher_text):
        decoded_message = b64decode(cipher_text.decode('utf8'))
        iv = decoded_message[:16]

        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        decrypted_message = cipher.decrypt(decoded_message[16:]).strip()
        decrypted_message = decrypted_message.decode('utf8')

        return decrypted_message