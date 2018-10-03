from block import Block
# from merkletree import MerkleTree
from typing import List

class BlockChain():
    class BlockNode():
        def __init__(self, block: Block, previous: 'BlockNode'):
            self.block: Block = block
            self.previous: 'BlockNode' = previous
            self.length = 1 if previous == None else previous.len+1
            self.next = []

        def add_next(self, next_block_node: 'BlockNode'):
            self.next.append(next_block_node)
        
        def __len__(self) -> int:
            return self.length


    def __init__(self, difficulty: bytes = b'\x00\x00'):
        genesis = Block.mine(b'0',[], b'\x00\x00')
        self.blocks = []
        self.blocks.append(self.BlockNode(genesis, None))
        self.latest_blocks = []
        self.latest_blocks.append(self.BlockNode(genesis, None))
        self.difficulty = difficulty
    
    def validate(self, block: Block, header: bytes) -> bool:
        if not (block.validate(self.difficulty)):
            # This checks both validate_hash(difficulty) and validate_root()
            return False
        if (block.get_header() == header):
            return True
        return False

    def get_matching_header(self, header: bytes) -> 'BlockNode':
        for end_block in reversed(self.latest_blocks):
            # end_blocks is a BlockNode
            if (header == end_block.block.get_header()):
                return end_block
        # The second for loop searches all blocks, if we reach this part we have a fork.
        for normal_block in reversed(self.blocks):
            # blocks is BlockNode
            if (header == normal_block.block.get_header()):
                return normal_block
        return None

    def add(self, block: Block):
        # Can raise exception instead of returning true or false
        found_node: 'BlockNode' = self.get_matching_header(block.get_header())
        if(found_node == None):
            return False
        if(self.validate(block, found_node.block.get_header())):
            self.blocks.append(self.BlockNode(block, found_node))
            self.latest_blocks.append(self.BlockNode(block, found_node))
            try: 
                self.latest_blocks.remove(found_node)
            except ValueError:
                print("Fork created.")
            return True
        return False
    
    # def get_latest_header(self) -> bytes:
    #     return self.latest_blocks.get_header()

    def mine_and_add(self, transactions: List[bytes]):
        
        pass
        # newblock = Block.mine(self.get_latest_header(), transactions, self.difficulty)
        # self.add(newblock)

    # def search_headers(self, header: bytes) -> int:
    #     for i, blocks in enumerate(self.blocks[::-1]):
    #         if(header == blocks.get_header()):
    #             return i
    #     return -1

if __name__ == "__main__":
    testblockchain = BlockChain()
    print(len(testblockchain.blocks))
    testblockchain.mine_and_add([b'1', b'2'])
    print(len(testblockchain.blocks))
    
    # Not sure how to test this blockchain, still need to implement forking
    # When forking, can we create another blockchain object? Or does the fork have to be contained in one blockchain object?
    # Do we have to implement UTXO transactions? If we do: 
    # What does it mean when you take input and output as transactions, do we pass in the function as an input? 
    # or is it the hash (/unique identifier) that we put in as input

    # For miner class: 
    # So the miner mines, then adds to the blockchain.
    # When do the transactions come into play?
    # How do we know which miner mined the block?
    # How do we raise the difficulty? through the nakamoto consensus? (everybody propagates an opinion?)
    # To test the miner, do we need to come up with a network of miners? (to broadcast newly mined blocks)
    # How do we send transactions around? Do we just send transactions to all miners?
    # Then hope all miners will add them in when they mine the next block?v 
    