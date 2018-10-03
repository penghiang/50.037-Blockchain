import hashlib
import time
import ecdsa


# Question 1
blockchaintext = "Blockchain Technology"
sha256 = hashlib.sha256(blockchaintext.encode('utf-8'))
sha512 = hashlib.sha512(blockchaintext.encode('utf-8'))
sha3256 = hashlib.sha3_256(blockchaintext.encode('utf-8'))
sha3512 = hashlib.sha3_512(blockchaintext.encode('utf-8'))
# print(sha256.hexdigest())
# print(sha512.hexdigest())
# print(sha3256.hexdigest())
# print(sha3512.hexdigest())


# Question 2
def hashfunc(n_bytes: int, inp) -> str:
    hashed = hashlib.sha512(inp.encode("utf-8"))
    n = n_bytes//8
    return hashed.hexdigest()[:n]

def compare(length: int, inp1, inp2):
    if(inp1[length] == inp2[length]):
        return True
    return False

clash = False
number = 0
hashes = []
start = time.time()
while (not clash):
    number += 1
    hashes.append(hashfunc(40, str(number)))
    if(hashes[-1] in hashes[:-1]):
        clash = True
        print(hashes[-1])
        print(number)
    if(number%10000 == 0):
        print(number)

print(time.time()-start)
# This happens pretty quickly.

def hashfuncbit(n_bits: int, inp: str) -> bytes:
    hashed = hashlib.sha512(inp.encode('utf-8'))
    return hashed.digest()[:n_bits]

# Just change the rawbit value
rawbit = b"\x00"*1
clash = False
number = 0
start = time.time()
while (not clash):
    number += 1
    if(hashfuncbit(40, str(number))[:len(rawbit)] == rawbit):
        print(number)
        clash = True
    if(number%600000 == 0):
        print(number)
print(time.time() - start)
#61 for 1 
#288946 for 2 zeroes, taking 0.76395s
#6899310 for 3 zeroes, taking 29.8574s
#3949194172 for 4 zeroes, taking 9937.515s


# Question 3
sk = ecdsa.SigningKey.generate()
vk = sk.get_verifying_key()
signature = sk.sign(b"Blockchain Technology")
assert vk.verify(signature, b"Blockchain Technology")



