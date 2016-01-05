import hashlib

def hash_str(s):
    return hashlib.md5(s).hexdigest()[0:12]

