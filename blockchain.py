from block import Block
# from merkletree import MerkleTree
from typing import List

class BlockChain():
    class BlockNode():
        # I think this class is quite unused, we're only using it for measuring the length.
        def __init__(self, block: Block, previous: 'BlockNode'):
            self.block: Block = block
            self.previous: 'BlockNode' = previous
            self.length = 1 if previous == None else previous.length+1
            # next is not really used.
            self.next = []
        
        # We are not using this method
        def add_next(self, next_block_node: 'BlockNode'):
            self.next.append(next_block_node)

    def __init__(self, difficulty: bytes = b'\x00\x00'):
        # genesis = Block.mine(b'0',[b''], b'\x00\x00')
        genesis = Block(b'0', b'0', 0.0, 151766)
        self.blocks: List['BlockNode'] = []
        self.blocks.append(self.BlockNode(genesis, None))
        self.latest_blocks = []
        self.latest_blocks.append(self.BlockNode(genesis, None))
        self.difficulty = difficulty
        self.orphans = []
        # orphans is block not blocknode

    # Validates 3 things:
    # The block's hash vs difficulty,
    # The transaction root of the block is made of transactions,
    # The previous header is as provided
    def validate(self, block: Block, prev_header: bytes) -> bool:
        if not (block.validate(self.difficulty)):
            # This checks both validate_hash(difficulty) and validate_root()
            return False
        if (block.prev_header == prev_header):
            return True
        return False

    # This method is unused
    def resolve(self) -> Block:
        return self.get_longest_chain().block

    # Searches for a matching header, returns the blocknode containing that header
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

    # Add searches for a header in the current list of nodes, and adds it to the relevant node
    # If no relevant header is found, adds to list of orphan nodes.
    # After adding, check all orphan nodes and automatically run .add() on them.
    def add(self, block: Block):
        # Can raise exception instead of returning true or false
        found_node: 'BlockNode' = self.get_matching_header(block.prev_header)
        if(found_node == None):
            # validating it again might be not necessary, just add it to the orphans
            if not (block.validate(self.difficulty)):
                return False
            print("Failed to find node in list, adding it to orphans")
            self.orphans.append(block)
            return True
        if(self.validate(block, found_node.block.get_header())):
            print("Validated new block, adding.")
            self.blocks.append(self.BlockNode(block, found_node))
            self.latest_blocks.append(self.BlockNode(block, found_node))
            try: 
                self.latest_blocks.remove(found_node)
            except ValueError:
                print("Fork created.")
            # for i in self.orphans[:]:
            #     if(i.prev_header == block.get_header()):
            #         self.add(i)
            #         self.orphans.remove(i)
            return True
        return False

    # Gets the longest chain.
    def get_longest_chain(self) -> 'BlockNode':
        longest = 0
        # curr_longest = None
        for blocknode in self.latest_blocks:
            if (blocknode.length > longest):
                longest = blocknode.length
                curr_longest = blocknode
        return curr_longest

    # Automatically finds the longest chain and mines.
    # The block returned is automatically already added to its own blockchain
    def mine(self, transactions: List) -> Block:
        longest = self.get_longest_chain()
        block = Block.mine(longest.block.get_header(), transactions, self.difficulty)
        print(block.get_header())
        return block

    def mine_once(self, transactions: List) -> Block:
        longest = self.get_longest_chain()
        block = Block.mine_once(longest.block.get_header(), transactions, self.difficulty)
        return block

    # This copy doesn't copy deep enough, but a deep copy has to go pretty deep
    # Not used.
    def get_copy(self) -> 'BlockChain':
        new_chain = BlockChain()
        new_chain.__dict__.update(self.__dict__)
        return new_chain

if __name__ == "__main__":
    # Difficulty is reduced for testing
    testdifficulty = b'\x00\x0f'
    testblockchain = BlockChain()
    testblockchain.difficulty = testdifficulty
    assert(len(testblockchain.blocks) == 1)
    assert(len(testblockchain.latest_blocks) == 1)

    # This is a test block
    testblock = Block.mine(testblockchain.latest_blocks[0].block.get_header(), [b'1', b'2'], testdifficulty)
    print("Mined testblock")
    testblock2 = Block.mine(testblock.get_header(), [b'33'], testdifficulty)
    print("Mined testblock2")

    # We continue mining,
    testblockchain.mine([b'23'])
    assert(len(testblockchain.blocks) == 2)
    assert(len(testblockchain.latest_blocks) == 1)

    # Then try adding an old mined block.
    testblockchain.add(testblock)
    assert(len(testblockchain.blocks) == 3)
    assert(len(testblockchain.latest_blocks) == 2)

    # We then add another old mined block.
    testblockchain.add(testblock2)
    assert(len(testblockchain.blocks) == 4)
    assert(len(testblockchain.latest_blocks) == 2)
    assert(testblockchain.get_longest_chain().length == 3)

    testblock3 = Block.mine(testblock2.get_header(), [b'34'], testdifficulty)
    print("Mined testblock3")
    testblock4 = Block.mine(testblock3.get_header(), [b'asd'], testdifficulty)
    print("Mined testblock4")
    
    # Testing orphans 
    testblockchain.add(testblock4)
    assert(len(testblockchain.orphans) == 1)
    assert(len(testblockchain.blocks) == 4)
    testblockchain.add(testblock3)
    assert(len(testblockchain.orphans) == 0)
    assert(len(testblockchain.blocks) == 6)
    assert(len(testblockchain.latest_blocks) == 2)
    assert(testblockchain.get_longest_chain().length == 5)
    testblockchain.mine([b'21'])
    assert(testblockchain.get_longest_chain().length == 6)

    # Validate time/timestamps

    # For miner class: 
    # How do we raise the difficulty? through the nakamoto consensus? (everybody propagates an opinion?)
    # To test the miner, do we need to come up with a network of miners? (to broadcast newly mined blocks)
    
    