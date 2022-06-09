import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
password = input(": ")
pwd = password.encode()
salt = b'\xe3"\xd735\xddB\xcd3\xb6-9\x11\x1b\x83\xe7'
kdf = PBKDF2HMAC(algorithm=hashes.SHA256, length=32, salt=salt, iterations=100000, backend=default_backend())
key = base64.urlsafe_b64encode(kdf.derive(pwd))
print(key)
