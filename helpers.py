#Thanks to Andres Torres for this code. Source: https://www.pythoncentral.io/hashing-strings-with-python/

import uuid
import hashlib

def hash_password(password):
    salt = uuid.uuid4().hex
    return hashlib.sha256(salt.encode() + password.encode()) + ':' + salt
