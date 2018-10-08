import time 
import json
import hashlib
import random
from typing import List
from merkletree import MerkleTree 

class Block():
    def __init__(self, prev_header: bytes, transaction_root=None, timestamp=None, nonce=None, transactions: MerkleTree=MerkleTree()):
        self.prev_header = prev_header
        # We are supposed to hash the transactions, get the root.
        self.transaction_root = transaction_root
        self.timestamp = timestamp
        self.nonce = nonce
        self.transactions = transactions

    def validate(self, difficulty: bytes) -> bool:
        # Still have to validate that the previous block's hash is correct
        if(self.timestamp != None):
            # Checks if there is a timestamp
            if Block.validate_root(self.transaction_root, self.transactions.get_entries()):
                # Checks the transaction_root
                if Block.validate_hash(self, difficulty):
                    # Checks if the header has a correct hash
                    return True
        return False
        
    @staticmethod
    def validate_root(root: bytes, transactions: List[bytes]) -> bool:
        return Block.get_transaction_root(transactions) == root

    @staticmethod
    def validate_hash(block: 'Block', difficulty: bytes) -> bool:
        json_string = block.to_json()
        _ = hashlib.sha256(json_string.encode('utf-8')).digest()
        difficulty += b'\xff'*(len(_)-len(difficulty))
        # Checks the hash,
        return (_ < difficulty)

    # @staticmethod
    # def validate_hash(block: 'Block', difficulty: int) -> bool:
    #     json_string = block.to_json()
    #     _ = hashlib.sha256(json_string.encode('utf-8')).digest()
    #     # Checks the hash,
    #     return (_[:difficulty] == b'\x00'*difficulty)

    # @classmethod
    # def from_json(block, json_string: str) -> 'Block':
    #     # Instantiates/Deserializes object from JSON string
    #     data = json.loads(json_string)
    #     newBlock = block(
    #         prev_header = data["prev_header"],
    #         transaction_header = data["transaction_header"],
    #         timestamp = data["timestamp"],
    #         nonce = data["nonce"]
    #     )
    #     return newBlock

    def to_json(self) -> str:
        json_dict = {
            "prev_header": self.prev_header.hex(),
            "transaction_root": self.transaction_root.hex(),
            "timestamp": self.timestamp, 
            "nonce": self.nonce
        }
        # Do we need to json this? or can we just simply concatenate
        return json.dumps(json_dict, sort_keys=True)

    def __eq__(self, otherBlock: 'Block'):
        # Check whether transactions are the same
        if(self.to_json() == otherBlock.to_json()):
            return True
        return False

    def get_header(self) -> bytes:
        json_str = self.to_json()
        return hashlib.sha256(json_str.encode('utf-8')).digest()

    def add_transaction(self, transaction: bytes):
        self.transactions.add(transaction)
        self.transaction_root = self.transactions.get_root()

    def add_transactions(self, transactions: List[bytes]):
        for i in transactions:
            self.transactions.add(i)
        self.transaction_root = self.transactions.get_root()

    @staticmethod
    def mine(prev_header: bytes, transactions: List, difficulty: bytes) -> 'Block':
        if(type(transactions[0]) != bytes):
            transactions_bytes = [x.to_json().encode() for x in transactions] 
            transtree = MerkleTree(transactions_bytes)
        else:
            transtree = MerkleTree(transactions)
        timestamp = time.time()
        nonce = random.randint(-2147483648, 2147483647)
        newblock = Block(prev_header, transtree.get_root() , timestamp, nonce, transtree)
        while(not Block.validate_hash(newblock, difficulty)):
            newblock.timestamp = time.time()
            newblock.nonce = random.randint(-2147483648, 2147483647)
            # nonce = nonce & 0b11111111111111111111111111111111
            # ensures a 32bit nonce
        return newblock

    @staticmethod
    def mine_once(prev_header: bytes, transactions: List[bytes], difficulty: bytes) -> 'Block':
        if(type(transactions[0]) != bytes):
            transactions_bytes = [x.to_json().encode() for x in transactions] 
            transtree = MerkleTree(transactions_bytes)
        else:
            transtree = MerkleTree(transactions)
        timestamp = time.time()
        nonce = random.randint(-2147483648, 2147483647)
        # nonce = nonce & 0b11111111111111111111111111111111
        # ensures a 32bit nonce
        newblock = Block(prev_header, transtree.get_root() , timestamp, nonce, transtree)
        if (Block.validate_hash(newblock, difficulty)):
            return newblock
        return None

    @staticmethod
    def get_transaction_root(transactions: List[bytes]) -> bytes:
        temp = MerkleTree()
        for i in transactions:
            temp.add(i)
        return temp.get_root()

if __name__ == "__main__":
    testdifficulty = b'\x00\x00'
    t1 = b'adsf'
    t2 = b'jdjd'
    t3 = b'kdsoo'
    testblock = Block(b'prev_header')
    testblock.add_transactions([t1,t2,t3])
    temproot = Block.get_transaction_root([t1,t2,t3])

    # tests if mine works, the header returned should start with 00
    tempblock = Block.mine(b'prev_header', [t1,t2,t3], testdifficulty)
    print(tempblock.get_header())

    x = hashlib.sha512("288946".encode('utf-8')).digest()
    assert(x[:2] == testdifficulty)
    y = Block.mine(b'123', [b"trans"], testdifficulty)
    print(y.nonce, y.timestamp, y.transaction_root, y.prev_header)
    # y should be validatable
    assert(y.validate(testdifficulty))

    # These 2 should be the same
    print(hashlib.sha256(y.to_json().encode('utf-8')).digest())
    print(y.get_header())