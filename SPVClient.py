from transaction import Transaction
from wallet import Wallet
import json
import hashlib
import ecdsa

# This class is not used.
class SPVClient():
    def __init__(self):
        self.wallet = Wallet()

    def send_money(self, receiver: bytes, amount: float) -> Transaction:
        receiver_key = ecdsa.VerifyingKey.from_string(receiver.decode())
        transaction = Transaction(
            self.wallet.get_public_key(),
            receiver_key,
            amount, 
            sender_key = self.wallet.sk
        )
        # When do i reduce the money from the wallet?
        return transaction

    def validate_header(self, header: str, difficulty: bytes) -> bool:
        hashed_bytes = hashlib.sha256(header.encode()).digest()
        difficulty += b'\xff'*(len(hashed_bytes)-len(difficulty))
        return (hashed_bytes < difficulty)

    def get_transaction_root(self, header: str) -> bytes:
        data = json.loads(header)
        return bytes.fromhex(data["transaction_root"])

    # verify_proof is imported from merkletree.
    
        

    # Network:
    # Request parents of orphans
    # Request transaction proof
    # Confirming transactions are in the blockchain
    # Request/broadcast block headers
    # Only sending block headers to SPVClients
    #   Identifying which network nodes are clients and which are miners. (can be hardcoded?)

    # Done: 
    # Send transactions and blocks
    # SPV client request amount (wallet)
    
