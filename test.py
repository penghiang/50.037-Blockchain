# Question 2
# It contains block objects 
# Blocks contain 
# Previous pointer, Nonce, Root, and Timestamp.
# Prev -> Points to previous block
# H(header) < target
# target = 00000fffff...ff
# Root -> Transaction set, hashed in the merkle tree.
# To validate block, we have to compute prev and root and nonce and hash it again.
# First block is genesis block, it's hardcoded

from block import Block
gen = Block(b'0', b'0', 0.0, 0)
while not (Block.validate_hash(gen, b'\x00\x00')):
    gen.nonce += 1

print(gen.nonce)

gen = Block(b'0', b'0', 0.0, 151766)
print(Block.validate_hash(gen, b'\x00\x00'))

import ecdsa
sk = ecdsa.SigningKey.generate()
vk = sk.get_verifying_key()
print(sk.__dict__)
print(sk.privkey.__dict__)
sk.sign(b"asd")
print(sk.__dict__)
print(sk.privkey.__dict__)
print(sk.to_string())
print(type(sk.to_string()))
