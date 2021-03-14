import socket
from base64 import b64decode, b64encode
from Cryptodome.Cipher import AES
import time
from Util.encryption import EncryptionHandler
import json

eH = EncryptionHandler(b'Sixteen byte key')

host,port = ('127.0.0.1', 10022)
mySocket = socket.socket()
mySocket.bind((host,port))
mySocket.listen()
conn,addr = mySocket.accept()
time.sleep(5)

conn.send(eH.encrypt_msg("sync"))
data = conn.recv(4096)
timeRecv = time.time()
response = json.dumps({'command' : 'CS', 'message': str(timeRecv) + '|' + str(time.time())})
conn.send(response.encode())
data = conn.recv(4096)
timeRecv = time.time()
print(eH.decrypt_message(data))

time.sleep(10)
conn.send(eH.encrypt_msg("start"))

while True:
    cipher_text = conn.recv(4096)
    decoded_message = b64decode(cipher_text.decode('utf8'))
    iv = decoded_message[:16]

    cipher = AES.new(b'Sixteen byte key', AES.MODE_CBC, iv)
    decrypted_message = cipher.decrypt(decoded_message[16:]).strip()
    # decrypted_message = decrypted_message.decode('utf8')
    print(decrypted_message)