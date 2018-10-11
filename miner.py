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
        self.balances: Dict[bytes, float] = {}
        self.wallet = Wallet()
        initial_transaction = Transaction(b'', self.wallet.get_public_key(), 100., "first transaction", signature=b'')
        self.transactions.append(initial_transaction)

        # initial_transaction needs to be verified 
        # I think we have to verify every transaction before mining..?
        # Need to implement first miner coinbase money
        # Need to have list of transactions to be put into merkle tree mined
        # Miners have to mine

        # Handle transactions so as to not repeat them in previously mined blocks or such, handle it in .add()?

        # Transactions should to be checked after and not rejected straight away, deposit might come later than withdrawal.
        # We should be able to implement only certain transactions that are good and reject the rest that are not.
        # Need to respond to other miners for queries about orphan's parents
        # Need to implement nakamoto consensus
        # Need to query for parents if too many orphans
        # Need to implement resolving other miner's longer blockchains (miner broadcasts block)
        # Good to make custom exceptions for failed verifications and the likes
        # Need to handle sending the same transactions: miners should check if the transaction has been sent before.
        # Miner needs to have data of all the wallets and how much money they contain to verify transactions.
        # Need to reject transactions made from shorter chains, and verify transactions from longer chains.
        # To resolve shorter forks, we can have a set of wallets/money for each fork, or we can compute on the fly.
        # What happens if miner receives 2 same transactions, should invalidate that
        # not required: miners joining halfway

        # Miners have to send through the network:-
        # transactions, blocks, difficulty raises, requests for orphans, 
        # Miner has to be coded to be interruptable by new incoming blocks
    

    def change_difficulty(self, difficulty: bytes):
        self.blockchain.difficulty = difficulty

    # Adds transactions to self.transactions
    # This is use for single transactions while verify_transactions is used for a list of transactions.
    # This does not yet update the balance, only when a block is mined the balance is updated.
    def add_transaction(self, transaction: Transaction):
        if(transaction.validate()):
            if(self.check_balances([transaction])):
                self.transactions.append(transaction)
                return True
        return False
                

    # Runs .validate() on all transactions, handles the first transaction differently.
    # Used in .receive_block(), when a block is received.
    # Does not check for signature of the first transaction as there isn't any. 
    # Verify purely validates transactions to see if they are able to go through, the adding is done later.
    # Does not tell which transactions are wrong, just whether the set is right or wrong.
    # Smartness can be added later, telling which are the rejected transactions.
    def verify_transactions(self, inp_transactions: List) -> bool:
        if(type(inp_transactions[0]) == bytes):
            transactions: List[Transaction] = [Transaction.from_json(x.decode()) for x in inp_transactions]
        else:
            transactions: List[Transaction] = inp_transactions
        # testbalances = copy.deepcopy(self.balances)
        if(transactions[0].amount == 100.0 and transactions[0].sender == b''):
            self.check_balances(transactions)
            for transaction in transactions[1:]:
                if (not transaction.validate()):
                    return False
            return True
        else:
            raise ValueError("First transaction: amount not 100 or sender not b''")

    # First updates all the transactions into a copy of current balances, 
    # Then checks if any balance is negative.
    # Returns False if any balance is negative, True otherwise.
    def check_balances(self, transactions: List[Transaction]) -> bool:
        testbalances = copy.deepcopy(self.balances)
        for i in transactions:
            self._update_balances(i, testbalances)
        for i in testbalances:
            if(testbalances[i] < 0):
                return False
        return True

    # Updates the provided balances, if no balances provided, self.balances is used 
    # Does not check if amount would be negative.
    # Should be used after/in self.check_balances() as this does not check.
    def _update_balances(self, inp_transaction: Transaction, balances: Dict=None):
        if (balances == None):
            balances = self.balances
        sender = inp_transaction.sender.to_string()
        receiver = inp_transaction.receiver.to_string()
        amount: float = inp_transaction.amount
        if not (sender in balances):
            balances[sender] = 0
        if not (receiver in balances):
            balances[receiver] = 0
        balances[sender] -= amount
        balances[receiver] += amount

        # if(sender in balances):
        #     if(balances[sender] >= inp_transaction.amount):
        #         balances[sender] -= inp_transaction.amount
        #         self._update_receiver_balance(receiver, inp_transaction.amount, balances)
        #         return True
        #     else:
        #         print("Sender doesn't have enough money")
        #         return False
        # print("Sender not registered in balance")
        # return False
    
    # Updates receiver balance, only used in _update_balances().
    def _update_receiver_balance(self, receiver: bytes, amount: float, balances: Dict):
        if(receiver in self.balances):
            balances[receiver] += amount
        else:
            balances[receiver] = amount

    # Gets the root of transactions after verifying them
    # Currently unused
    def get_root(self) -> bytes:
        if(self.verify_transactions(self.transactions)):
            transactions_bytes = [x.to_json().encode() for x in self.transactions]
            return Block.get_transaction_root(transactions_bytes)

    # Receives block from other miners
    # Validates the new block, then add it into the blockchain.

    # Just whether it can go through or cannot go through, it's ok if update balances is repeated??
    # I check, then if it's good, 
    # I'll add the block and update my balances and update my wallet and remove repeated transactions
    # ._add_block() is useless now
    # To be more efficient, I could store my output of verify_transactions, of the new balance and replace it
    def receive_block(self, block: Block) -> bool:
        verified = self.verify_transactions(block.transactions.get_entries())
        if (verified):
            if(block.validate(self.blockchain.difficulty)):
                self.blockchain.add(block)
                # update balance, but inefficiency
                self._update_balances(block.transactions.get_entries())
                self._update_self_wallet(block.transactions.get_entries())
                self.remove_repeated_transactions(block.transactions.get_entries())
                return True
            else:
                raise ValueError("Failed to validate block")
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
        for i, self_transaction in enumerate(self.transactions[1:]):
            for other_transaction in transactions:
                if(self_transaction.to_json() == other_transaction.to_json()):
                    # Since we've implemented __eq__, we can just do 
                    # self_transaction == other_transaction
                    print("Removed a transaction")
                    leftovers.pop(i)
        self.transactions = leftovers

    # Broadcasts block to other miners
    def send_block(self):
        pass

    # This mines and adds the block, returns the new block mined to be broadcasted.
    # To verify transactions, we used .receive_block(). 
    # If it returns false the transactions have an issue, which shouldn't happen as self.transactions are already validated
    def mine(self) -> Block:
        newblock = self.blockchain.mine(self.transactions)
        if not (self.receive_block(newblock)): # This shouldn't return false...
            raise ValueError("Block not received properly after mining, probably some transactions are wrong")
        return newblock

    # Private method used in mine() and receive_block(), for doing some actions to add a block.
    # update transactions should be here.
    # Not used, implementation is put in receive_block
    def _add_block(self, newblock: Block):
        self.blockchain.add(newblock)
        self._update_self_wallet(newblock.transactions.get_entries())
        self.remove_repeated_transactions(newblock.transactions.get_entries())

    # Used in _add_block, to update self.wallet with transactions
    def _update_self_wallet(self, transactions: List):
        for trans in transactions:
            transaction = Transaction.from_json(trans.decode())
            if (transaction.receiver.to_string() == self.wallet.get_public_key().to_string()):
                self.wallet.deposit(transaction.amount)
            if (transaction.sender.to_string() == self.wallet.get_public_key().to_string()):
                if not (self.wallet.withdraw(transaction.amount)):
                    # Not enough cash from wallet, shouldn't happen.
                    # Transactions should have been validated in .receive_blocks()
                    raise ValueError("Not enough money, shouldn't happen")
        

    

        
    

if __name__ == '__main__':
    miner1 = Miner()
    miner2 = Miner()
    print(miner1.wallet.get_public_key().to_string() == miner2.wallet.get_public_key().to_string())
    print(len(miner1.blockchain.blocks))
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

    assert(miner1.receive_block(testblock))
    print(len(miner2.blockchain.blocks))
    print(len(miner2.transactions), "asdf")
    miner2.receive_block(testblock)

    print(len(miner1.blockchain.blocks))
    print(len(miner2.blockchain.blocks))

    miner2.add_transaction(testtransaction)
    miner1.add_transaction(testtransaction)
    print(len(miner1.transactions), len(miner2.transactions), "asdf")
    testblock2 = miner2.mine()
    print(len(miner1.blockchain.blocks))
    miner1.receive_block(testblock2)
    print(len(miner1.blockchain.blocks))
    print(len(miner1.transactions), len(miner2.transactions), "asdf")
    
    