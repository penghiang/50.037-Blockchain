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