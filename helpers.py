#Thanks to Andres Torres for this code. Source: https://www.pythoncentral.io/hashing-strings-with-python/

import uuid
import hashlib

#Takes string, hashes it with SHA256 and random salt, returns a hashed string ending with the salt
def hash_password(password):
    salt = uuid.uuid4().hex
    return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt

#Takes a hashed password (from password DB) and a password provided by the user
#Hashes second password with same salt, and returns true if hashes match; false otherwise
def check_password(hashed_password, user_password):
    password, salt = hashed_password.split(':')
    return password == hashlib.sha256(salt.encode() + user_password.encode()).hexdigest()
