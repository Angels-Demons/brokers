import base64

from django.test import TestCase
import hashlib
# Create your tests here.

token = "b1e6c9af8560db161e17be9e552839c1"


def behsa_generated_pass():
    return behsa_hash("13001447" + '|' + "E@123456" + '|' + token)



def behsa_hash(hash_string):
    byte_hash = hash_string.encode()
    md5hash = hashlib.md5(byte_hash).hexdigest()
    return md5hash.replace("-", "")




def localBasic( username, password):
    userpass = username + ":" + password
    encodedBytes = base64.b64encode(userpass.encode("utf-8"))
    encodedStr = "Basic " +str(encodedBytes, "utf-8")
    return encodedStr


print(behsa_generated_pass())
print(localBasic("broker_0","broker_0pass"))