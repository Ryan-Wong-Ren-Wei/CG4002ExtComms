import socket

from Cryptodome.Cipher import AES
 
def Main():
        host = "127.0.0.1"
        port = 10022
        
        mySocket = socket.socket()
        mySocket.bind((host,port))
        
        mySocket.listen(1)
        conn, addr = mySocket.accept()
        print ("Connection from: " + str(addr))

        KEY = b'\x01\x80\xba\x82\x7a\xc8\x7a\x3a\x26\xf1\xca\xc6\x9e\x1c\x3c\xbe'
        while True:
                nonce, ciphertext, tag = conn.recv(1024).decode()
                if not (ciphertext and nonce and tag):
                        break
                cipher = AES.new(KEY, AES.MODE_EAX, nonce=nonce)
                plaintext = cipher.decrypt(ciphertext)
                try:
                        cipher.verify(tag)
                        print("The message is authentic:", plaintext)
                except ValueError:
                        print("Key incorrect or message corrupted")
                # print ("from connected  user: " + str(plaintext))
                plaintext = plaintext.upper()
                print ("sending: " + str(plaintext))
                conn.send(plaintext.encode())
                
        conn.close()
     
if __name__ == '__main__':
    Main()