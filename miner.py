from block import Block
from typing import List, Dict
from wallet import Wallet
from blockchain import BlockChain
from transaction import Transaction
import copy
# import ecdsa

class Miner():
    def __init__(self, blockchain: BlockChain=None):
        self.blockchain = BlockChain()
        if(blockchain != None):
            # This refers to the same blockchain object, but we just want a copy of it. 
            self.blockchain = blockchain
        self.transactions = []
        # self.balances: List[Dict[bytes, float]] = [{}]
        # self.balances: Dict[bytes, float] = {}
        # It's a dictionary of a dictionary.
        # First keys are blocks => headers, second keys are sender/receiver's keys
        self.balances: Dict[bytes, Dict[bytes, float]] = {}
        self.wallet = Wallet()
        initial_transaction = Transaction(b'', self.wallet.get_public_key(), 100., "first transaction", signature=b'')
        self.transactions.append(initial_transaction)

        # Done:
        # initial_transaction needs to be verified 
        # I think we have to verify every transaction before mining..?
        # Need to implement first miner coinbase money
        # Need to have list of transactions to be put into merkle tree mined
        # Miners have to mine
        # Handle transactions so as to not repeat them in previously mined blocks or such, handle it in .add()?
        # Since searching for the longest chain is relatively cheap, especially if there are little forks, we 
        #   can search for the longest chain every time instead of storing the current longest chain.
        # We're using a on-the-fly calculation of balances, with some memory storage done every 5 blocks.
        # Miner needs to have data of all the wallets and how much money they contain to verify transactions.


        # Not done:
        # When we reject transactions/blocks from forks, should we pick up the transactions to be resubmitted again?
        # Transactions should to be checked after and not rejected straight away, deposit might come later than withdrawal.
        # We should be able to implement only certain transactions that are good and reject the rest that are not.
        # Need to respond to other miners for queries about orphan's parents
        # Need to implement nakamoto consensus
        # Need to query for parents if too many orphans
        # Need to implement resolving other miner's longer blockchains (miner broadcasts block)
        # Good to make custom exceptions for failed verifications and the likes
        # Need to handle sending the same transactions: miners should check if the transaction has been sent before.
        # Need to reject transactions made from shorter chains, and verify transactions from longer chains.
        # not required: miners joining halfway

        # Miners have to send through the network:-
        # transactions, blocks, difficulty raises, requests for orphans, 
        # Miner has to be coded to be interruptable by new incoming blocks
    

    def change_difficulty(self, difficulty: bytes):
        self.blockchain.difficulty = difficulty

    # Adds transactions to self.transactions
    # This is used for single transactions while validate_transactions is used for a list of transactions.
    # This does not yet update the balance, only when a block is mined the balance is updated.
    # If the transaction is rejected, the transaction is thrown away instead of being put into an orphan pool.
    def add_transaction(self, transaction: Transaction):
        if(transaction.validate()):
            current_balance = self.get_current_balance()
            if(self.check_balances([transaction], current_balance)):
                self.transactions.append(transaction)
                return True
        return False
                

    # Runs .validate() on all transactions, handles the first transaction differently.
    # Used in .receive_block(), when a block is received.
    # Does not check for signature of the first transaction as there isn't any. 
    # Verify only validates transactions to see if they are able to go through, the adding is done later.
    # Does not tell which transactions are wrong, just whether the set is right or wrong.
    def validate_transactions(self, inp_transactions: List, balance_to: Dict[bytes,float]) -> bool:
        if(type(inp_transactions[0]) == bytes):
            transactions: List[Transaction] = [Transaction.from_json(x.decode()) for x in inp_transactions]
        else:
            transactions: List[Transaction] = inp_transactions
        if(transactions[0].amount == 100.0 and transactions[0].sender == b''):
            if not (self.check_balances(transactions, balance_to)):
                return False
            for transaction in transactions[1:]:
                if (not transaction.validate()):
                    return False
            return True
        else:
            raise ValueError("First transaction: amount not 100 or sender not b''")

    # First updates all the transactions into a copy of current balances, 
    # Then checks if any balance is negative.
    # Returns False if any balance is negative, True otherwise.
    # Does not check b''
    def check_balances(self, transactions: List[Transaction], balance: Dict[bytes, float]) -> bool:
        testbalances = copy.deepcopy(balance)
        for i in transactions:
            self._update_balances(i, testbalances)
        for i in testbalances:
            if(i == b''):
                continue
            if(testbalances[i] < 0):
                return False
        return True

    # Updates the provided balances with inp_transaction
    # Mutates the passed-in dictionary
    # Does not check if amount would be negative.
    # Should be used after/in self.check_balances() as this does not check.
    def _update_balances(self, inp_transaction: Transaction, balances: Dict[bytes, float]):
        sender = inp_transaction.sender if inp_transaction.sender == b'' else inp_transaction.sender.to_string()
        receiver = inp_transaction.receiver.to_string()
        amount: float = inp_transaction.amount
        if not (sender in balances):
            balances[sender] = 0
        if not (receiver in balances):
            balances[receiver] = 0
        balances[sender] -= amount
        balances[receiver] += amount

    # Gets the root of transactions after verifying them
    # Currently unused
    # def get_root(self) -> bytes:
        # if(self.validate_transactions(self.transactions)):
        #     transactions_bytes = [x.to_json().encode() for x in self.transactions]
        #     return Block.get_transaction_root(transactions_bytes)

    # Receives block from other miners
    # Validates the new block, then add it into the blockchain.
    # I check the received block, then if it's good, 
    #   I'll add the block and update my balances and update my wallet and remove repeated transactions
    def receive_block(self, block: Block) -> bool: 
        # We need to handle errors for prev_header not being there.
        balance = self.compute_balance(block.prev_header)
        if(balance is None):
            # It's an orphan
            self.blockchain.add(block)
            return False

        verified = self.validate_transactions(block.transactions.get_entries(), balance)
        if (verified):
            if(block.validate(self.blockchain.difficulty)):
                for i in block.transactions.get_entries():
                    self._update_balances(Transaction.from_json(i), balance)
                self.blockchain.add(block)
                self._update_self_wallet(block.transactions.get_entries())
                self.remove_repeated_transactions(block.transactions.get_entries())
                # After 5(arbitrary number) blocks, stores computed balance in self.balances for efficiency
                if (self.blockchain.blocks[-1].length % 5 == 0):
                    self.balances[block.get_header()] = self.compute_balance(block.get_header())
                return True
            else:
                print("Failed to validate block")
                return False
                # raise ValueError("Failed to validate block")
        # raise ValueError("failed to verify transactions")
        return False

    # removes all transactions that appear in both the input and self.transactions
    # To be used before adding a new block (self._add_block())
    def remove_repeated_transactions(self, input_transaction: List):
        if(type(input_transaction[0]) == bytes):
            transactions = [Transaction.from_json(x.decode()) for x in input_transaction]
            # I'm converting from json to json again, it's an inefficiency
        else:
            transactions: List[Transaction] = input_transaction
        leftovers = self.transactions[:]
        to_be_popped: List[int] = []
        for i, self_transaction in enumerate(self.transactions[1:]):
            for other_transaction in transactions:
                if(self_transaction.to_json() == other_transaction.to_json()):
                    # Since we've implemented __eq__, we can just do 
                    # self_transaction == other_transaction
                    print("Removed a transaction")
                    to_be_popped.append(i+1)
        for i in to_be_popped[::-1]:
            # We're popping from the back
            leftovers.pop(i)
        self.transactions = leftovers

    # Broadcasts block to other miners
    def send_block(self):
        pass

    # This mines and adds the block, returns the new block mined to be broadcasted.
    # To verify transactions, we used .receive_block(). 
    # If it errors the transactions have an issue, which shouldn't happen as self.transactions are already validated
    def mine(self) -> Block:
        newblock = self.blockchain.mine(self.transactions)
        if not (self.receive_block(newblock)): # This shouldn't raise an error...
            raise ValueError("Block not received properly after mining, probably some transactions are wrong")
        return newblock

    # Attempts to mine once, so we are able to interrupt the mining.
    # Returns None if it fails to get a valid block.
    def mine_once(self) -> Block:
        newblock = self.blockchain.mine_once(self.transactions)
        if (newblock is not None):
            if not (self.receive_block(newblock)): # This shouldn't raise an error...
                raise ValueError("Block not received properly after mining, probably some transactions are wrong")
            return newblock
        return None
    

    # Private method used in mine() and receive_block(), for doing some actions to add a block.
    # update transactions should be here.
    # Not used, implementation is put in receive_block
    # def _add_block(self, newblock: Block):
    #     self.blockchain.add(newblock)
    #     self._update_self_wallet(newblock.transactions.get_entries())
    #     self.remove_repeated_transactions(newblock.transactions.get_entries())

    # To update self.wallet with transactions
    def _update_self_wallet(self, transactions: List):
        for trans in transactions:
            transaction = Transaction.from_json(trans.decode())
            if (transaction.receiver.to_string() == self.wallet.get_public_key().to_string()):
                self.wallet.deposit(transaction.amount)
            if (transaction.sender == b''):
                continue
            elif (transaction.sender.to_string() == self.wallet.get_public_key().to_string()):
                if not (self.wallet.withdraw(transaction.amount)):
                    # Not enough cash from wallet, shouldn't happen.
                    # Transactions should have been validated in .receive_blocks()
                    raise ValueError("Not enough money, shouldn't happen")
    
    # This function verifies that the transaction exists in the blockchain
    # This function will return the proof.
    # Should be used for clients.
    def verify_transaction(self, transaction):
        transaction: bytes = transaction.to_json().encode()
        current_block = self.blockchain.get_longest_chain()
        while current_block != None:
            proof = current_block.block.transactions.get_proof(transaction)
            if proof != None:
                return proof
            current_block = current_block.previous
        return None

    # Computes the balance from the stated header to the genesis block.
    # Computes the balance on the fly, can be used in forking or verification.
    # Assumes the header provided is good.
    # Makes use of self.balances to reduce computation. (kinda like checkpoints)
    def compute_balance(self, header: bytes) -> Dict[bytes,float]:
        current_node = self.blockchain.get_matching_header(header)
        if (current_node == None):
            return None
        balance = {}
        while (current_node != None):
            if(current_node.block.get_header() in self.balances):
                return self.combine_balances(self.balances[current_node.block.get_header()], balance)
            current_transactions = current_node.block.transactions.get_entries()
            for transaction in current_transactions:
                trans = Transaction.from_json(transaction)
                self._update_balances(trans, balance)
            current_node = current_node.previous
        return balance

    # Gets the longest chain's balance.
    def get_current_balance(self) -> Dict[bytes, float]:
        current_longest_chain_header = self.blockchain.get_longest_chain().block.get_header()
        return self.compute_balance(current_longest_chain_header)


    # Given 2 balances, adds them together.
    def combine_balances(self, inp_balances1, inp_balances2):
        balances1 = copy.deepcopy(inp_balances1)
        balances2 = copy.deepcopy(inp_balances2)
        for i in balances1:
            if(i in balances2):
                balances2[i] += balances1[i]
            else:
                balances2[i] = balances1[i]
        return balances2

    # Checks for orphans in self.blockchain, and attempts to add all of them in a for loop.
    def add_orphans(self):
        for orphan in self.blockchain.orphans[:]:
            if(self.receive_block(orphan)):
                self.blockchain.orphans.remove(orphan)
                print("Orphan added to blockchain!")
                
        
    


                


    
    
    

        
    

if __name__ == '__main__':
    miner1 = Miner()
    miner2 = Miner()
    assert(miner1.wallet.get_public_key().to_string() != miner2.wallet.get_public_key().to_string())
    assert(len(miner1.blockchain.blocks)==1)
    first_transaction = Transaction(b'', miner2.wallet.get_public_key(), 100., "first transaction", signature=b'')
    testtransaction = Transaction(
        miner2.wallet.get_public_key(),
        miner1.wallet.get_public_key(),
        1.,
        sender_key=miner2.wallet.sk
    )
    
    testblock = Block.mine(
        miner1.blockchain.latest_blocks[-1].block.get_header(),
        [first_transaction,testtransaction],
        b'\x00\x00'
    )

    testtransaction2 = Transaction(
        miner2.wallet.get_public_key(),
        miner1.wallet.get_public_key(),
        1.1,
        sender_key=miner2.wallet.sk
    )

    # After mining a block and having a few test transactions, we send it to miners.

    assert(miner1.receive_block(testblock))
    assert(len(miner2.blockchain.blocks)==1)
    assert(miner2.transactions[0].sender == b'')
    assert(miner2.transactions[0].receiver == miner2.wallet.get_public_key())
    # miner2's first transaction should still be the coinbase one
    miner2.receive_block(testblock)

    assert(len(miner1.blockchain.blocks)==2)
    assert(len(miner2.blockchain.blocks)==2)
    # miner1 and miner2 should have both added the transactions to block.

    miner2.add_transaction(testtransaction2)
    miner1.add_transaction(testtransaction2)
    assert(len(miner1.transactions) == 2)
    assert(len(miner2.transactions) == 2)
    testblock2 = miner2.mine()
    assert(len(miner1.transactions)==2)
    assert not (miner1.verify_transaction(testtransaction2))
    # This tests verify_transaction.
    miner1.receive_block(testblock2)
    assert (miner1.verify_transaction(testtransaction2))
    assert(len(miner1.transactions)==1)
    assert(len(miner1.blockchain.blocks)==3)
    assert(len(miner1.transactions) == len(miner2.transactions))

    # This tests if verify_transaction still works if transaction is in previous block
    testblock3 = miner1.mine()
    assert(miner1.verify_transaction(testtransaction) == miner2.verify_transaction(testtransaction))
    
    testtransaction3 = Transaction(
        miner2.wallet.get_public_key(),
        miner1.wallet.get_public_key(),
        1000,
        sender_key=miner2.wallet.sk
    )
    assert not (miner1.add_transaction(testtransaction3))
    assert (len(miner1.transactions)==1)
    testblock4 = Block.mine(
        miner1.blockchain.latest_blocks[-1].block.get_header(),
        [first_transaction,testtransaction3],
        b'\x00\x00'
    )
    # Tests rejecting invalid block.
    assert not (miner1.receive_block(testblock4))


    # Tests if orphaning works. At this stage, we have to manually run .add_orphans()
    #   But it could easily be automated.
    testblock5 = miner1.mine()
    assert not (miner2.receive_block(testblock5))
    assert(miner2.receive_block(testblock3))
    assert(len(miner2.blockchain.orphans)==1)
    miner2.add_orphans()
    assert(len(miner2.blockchain.blocks)==5)
    assert(len(miner2.blockchain.orphans)==0)

    # Extra checks: Check balances, check forks and their balances.