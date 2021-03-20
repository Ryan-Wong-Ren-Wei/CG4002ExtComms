from Util.encryption import EncryptionHandler

h = EncryptionHandler(b'Sixteen Byte Key')

message = "caleb"
em = h.encrypt_msg(message)
print(h.decrypt_message(em))
print(b"R\x9e\xc6!\x01\x05\xcf\xa6&\xac\x9dQ\xc8\x92\xe5\xb4".decode('utf8'))