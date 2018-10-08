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
        initial_transaction = Transaction(b'', self.wallet.get_public_key(), 100, "first transaction", signature=b'')
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
    @staticmethod
    def verify_transactions(inp_transactions: List) -> bool:
        if(type(inp_transactions[0]) == bytes):
            transactions = [Transaction.from_json(x.decode()) for x in inp_transactions]
        else:
            transactions = inp_transactions
        if(transactions[0].amount == 100 and transactions[0].sender == b''):
            for transaction in transactions[1:]:
                if (not transaction.validate()):
                    return False
            return True
        else:
            raise ValueError("First transaction amount not 100 or sender not b''")

    def get_root(self) -> bytes:
        if(self.verify_transactions(self.transactions)):
            transactions_bytes = [x.to_json().encode() for x in self.transactions]
            return Block.get_transaction_root(transactions_bytes)

    # Receives block from other miner
    def receive_block(self, block: Block) -> bool:
        verified = self.verify_transactions(block.transactions.dataentries)
        if (verified):
            if(block.validate(self.blockchain.difficulty)):
                self.blockchain.add(block)
                return True
            else:
                raise ValueError("Failed to validate block")
        raise ValueError("failed to verify transactions")
        return False

    # Broadcasts block to other miners
    def send_block(self):
        pass


if __name__ == '__main__':
    miner1 = Miner()
    miner2 = Miner()
    first_transaction = Transaction(b'', miner2.wallet.get_public_key(), 100, "first transaction", signature=b'')
    testtransaction = Transaction(miner2.wallet.get_public_key(),miner1.wallet.get_public_key(),1, sender_key=miner2.wallet.get_private_key())
    
    testblock = Block.mine(miner1.blockchain.latest_blocks[-1].block.get_header(),[first_transaction,testtransaction], b'\x00\x00')
    assert(miner1.receive_block(testblock))
    print(len(miner1.blockchain.blocks))
        
    
    