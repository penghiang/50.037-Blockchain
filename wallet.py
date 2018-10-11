import ecdsa 

# We did not implement signing from wallet, signing is done with Transaction.sign(key)
# instead of Wallet.sign(transaction)
class Wallet():
    def __init__(self):
        self.sk = ecdsa.SigningKey.generate()
        self.vk = self.sk.get_verifying_key()
        self.balance = 0.0
    
    def get_public_key(self):
        return self.vk

    def get_amount(self):
        return self.balance
    
    def withdraw(self, amount: float) -> bool:
        if(self.balance > amount):
            self.balance -= amount
            return True
        return False
    
    def deposit(self, amount: float):
        self.balance += amount
