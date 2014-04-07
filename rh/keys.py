import os
import hashlib

def generate_api_key(prefix):
    sha1 = hashlib.sha1()
    sha1.update(os.urandom(8))
    h = sha1.hexdigest()[:20]
    return '%s_%s' % (prefix, h)
