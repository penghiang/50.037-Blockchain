from blockchain import BlockChain
from block import Block
from wallet import Wallet
from transaction import Transaction
from typing import List
import ecdsa

class Miner():
    def __init__(self):
        self.blockchain = BlockChain()
        self.transactions = []
        self.wallet = Wallet()
        initial_transaction = Transaction(b'', self.wallet.get_public_key(), 100, "first transaction")
        self.transactions.append(initial_transaction)

        # initial_transaction needs to be verified 
        # I think we have to verify every transaction before mining..?
        # Need to implement first miner coinbase money
        # Need to have list of transactions to be put into merkle tree mined


        # Need to contain open transactions/unspent coins if UTXO
        # Need to respond to other miners for queries about orphan's parents
        # Need to implement nakamoto consensus
        # Need to query for parents if too many orphans
        # Need to implement resolving other miner's longer blockchains (miner broadcasts block)
    

    def raise_difficulty(self, difficulty: bytes):
        self.blockchain.difficulty = difficulty

    
    def add_transaction(self, transaction: Transaction):
        # We are checking transactions twice for no reason?? Once here and once in verify_transactions()
        if(transaction.validate()):
            self.transactions.append(transaction)

    # Runs .validate() on all transactions, handles the first transaction differently.
    # Does not check for signature of the first transaction as there isn't any. 
    def verify_transactions(self, transactions: List[Transaction]) -> bool:
        if(transactions[0].amount == 100 and transactions[0].sender == b''):
            for transaction in transactions:
                if (not transaction.validate()):
                    return False
            return True
        else:
            return False

    # Receives block from other miner
    def receive_block(self, block: Block) -> bool:
        verified = self.verify_transactions(block.transactions.dataentries)
        if (verified):
            if(block.validate(self.blockchain.difficulty)):
                self.blockchain.add(block)
                return True
        return False

    # Broadcasts block to other miners
    def send_block(self):
        pass


if __name__ == '__main__':
    miner1 = Miner()
    miner2 = Miner()
    testtransaction = Transaction(miner2.wallet.get_public_key(),miner1.wallet.get_public_key(),1, sender_key=miner2.wallet.get_private_key())
    testblock = Block.mine(miner1.blockchain.latest_blocks[-1].block.get_header(),[testtransaction], b'\x00\x00')
    assert(miner1.receive_block(testblock))
    print(len(miner1.blockchain.blocks))
        
    
    