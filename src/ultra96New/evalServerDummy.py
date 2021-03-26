import socket
import base64
from Crypto.Cipher import AES
import sys
ACTIONS = ['gun', 'sidepump', 'hair']
POSITIONS = ['1 2 3', '3 2 1', '2 3 1', '3 1 2', '1 3 2', '2 1 3']
MESSAGE_SIZE = 3

def decrypt_message(cipher_text):
        decoded_message = base64.b64decode(cipher_text)
        iv = decoded_message[:16]
        secret_key = bytes(str('Sixteen byte key'), encoding="utf8") 
        # print("HI")
        cipher = AES.new(secret_key, AES.MODE_CBC, iv)
        decrypted_message = cipher.decrypt(decoded_message[16:]).strip()
        decrypted_message = decrypted_message.decode('utf8')

        decrypted_message = decrypted_message[decrypted_message.find('#'):]
        decrypted_message = bytes(decrypted_message[1:], 'utf8').decode('utf8')

        messages = decrypted_message.split('|')
        position, action, sync = messages[:MESSAGE_SIZE]
        return {
            'position': position, 'action': action, 'sync':sync
        }

if __name__ == "__main__":
    if len(sys.argv) == 3:
        host = sys.argv[1].strip()
        port = int(sys.argv[2].strip())
    else:
        host = "127.0.0.1"
        port = 8888
    mySocket = socket.socket()
    mySocket.bind((host,port))
    mySocket.listen(1)
    conn,addr= mySocket.accept()

    print("Connection established with: ", conn)

    while True:
        data = conn.recv(1024)
        if data:
            try:
                msg = data.decode("utf8")
                print(f"msg", {msg})
                decrypted_message = decrypt_message(msg)
                if decrypted_message['action'] == "logout":
                    print("logout")
                    conn.close()
                    sys.exit()
                elif len(decrypted_message['action']) == 0:
                    pass  # no valid action sent
                else:  # action is available so we log it
                    print("{} :: {} :: {}".format(decrypted_message['position'],
                                                                decrypted_message['action'], 
                                                                decrypted_message['sync']))
                    conn.sendall(str(['1','2','3']).encode())
            
            except Exception as e:
                print(e)