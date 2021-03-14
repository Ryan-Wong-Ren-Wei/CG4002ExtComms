import socket
from base64 import b64decode, b64encode
from Cryptodome.Cipher import AES

host,port = ('127.0.0.1', 10022)
mySocket = socket.socket()
mySocket.bind((host,port))
mySocket.listen()
conn,addr = mySocket.accept()

while True:
    cipher_text = conn.recv(4096)
    decoded_message = b64decode(cipher_text.decode('utf8'))
    iv = decoded_message[:16]

    cipher = AES.new(b'Sixteen byte key', AES.MODE_CBC, iv)
    decrypted_message = cipher.decrypt(decoded_message[16:]).strip()
    # decrypted_message = decrypted_message.decode('utf8')
    print(decrypted_message)