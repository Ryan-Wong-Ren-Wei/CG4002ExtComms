import socket
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad
from Cryptodome.Random import get_random_bytes
from base64 import b64encode, b64decode, decode
from getpass import getpass
import json

# Class to handle AES encryption and decryption, initialized at start with secret sixteen bit key
class EncryptionHandler():

    def __init__(self, key: bytes):
        self.key = key

    def encrypt_msg(self, message):
        cipher = AES.new(self.key, AES.MODE_CBC)
        message += ' ' * (16 - len(message) % 16)
        ct_bytes = cipher.encrypt(message.encode('utf8'))
        iv = cipher.iv
        # json_bytes = json.dumps({'iv': iv, 'ciphertext': ct}).encode()
        print(iv + ct_bytes)
        encryptedMessage = b64encode(iv + ct_bytes)
        print("Encrypted: ", encryptedMessage)
        return encryptedMessage

    def decrypt_message(self, cipher_text):
        decoded_message = b64decode(cipher_text.decode('utf8'))
        print("Decoded: ", decoded_message[16:])
        iv = decoded_message[:16]
        print(iv)

        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        print(self.key)
        decrypted_message = cipher.decrypt(decoded_message[16:]).strip()
        print("1", decrypted_message)
        decrypted_message = decrypted_message.decode('utf8')
        print("2", decrypted_message)

        return decrypted_message