import json
import ecdsa

# Question 4
sk = ecdsa.SigningKey.generate()
vk = sk.get_verifying_key()

sk2 = ecdsa.SigningKey.generate()
vk2 = sk2.get_verifying_key()

# Where/how do we check account balance?
# We create a new wallet class maybe
# Need to ensure that coins cannot be double-spent

class Transaction():
    def __init__(self, sender, receiver, amount: float, comment: str ='', signature=None, sender_key=None):
        # Sender and receivers are public keys
        # There might be no signature or string or sender_key
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.comment = comment
        self.signature = signature
        if(sender_key != None):
            self.signature = self.sign(sender_key)

    def to_json(self) -> str:
        # Serializes object to JSON string
        if(self.sender == None or self.sender == b''):
            sender_string = ''
        else:
            sender_string = self.sender.to_string().hex()
        json_dict = {
            "sender": sender_string, "receiver": self.receiver.to_string().hex(),
            "amount": self.amount,
            "signature": self.signature.hex(), "comment": self.comment
            }
        return json.dumps(json_dict, sort_keys=True)

    def to_json_no_sig(self) -> str:
        # Same as to_json, but signature field is left empty.
        # This function is useful for verifying and signing.
        if(self.sender == None or self.sender == b''):
            sender_string = ''
        else:
            sender_string = self.sender.to_string().hex()
        json_dict = {
            "sender": sender_string, "receiver": self.receiver.to_string().hex(),
            "amount": self.amount,
            "signature": '', "comment": self.comment
            }
        return json.dumps(json_dict, sort_keys=True)

    @classmethod
    def from_json(trscn, jsonstring: str) -> 'Transaction':
        # Instantiates/Deserializes object from JSON string
        # Does not validate the signature
        data = json.loads(jsonstring)
        sender = data["sender"]
        if(sender != ''):
            sender = ecdsa.VerifyingKey.from_string(bytes.fromhex(data["sender"]))
        else: 
            sender = b''
        newTransaction = trscn(
            sender = sender,
            receiver = ecdsa.VerifyingKey.from_string(bytes.fromhex(data["receiver"])),
            amount = data["amount"],
            comment = data["comment"],
            signature = bytes.fromhex(data["signature"])
        )
        return newTransaction

    def sign(self, private_key):
        # returns a signed transaction
        # Sign object with private key passed
        # Used in __init__ if private_key is provided during declaration of new Transaction
        json_string = self.to_json_no_sig()
        signed_transaction = private_key.sign(json_string.encode('utf-8'))        
        return signed_transaction
        
    def validate(self) -> bool:
        # Validate transaction correctness.
        # Returns false if the signature is wrong.
        json_string = self.to_json_no_sig()
        try:
            if(self.signature == None or self.signature == b'' or self.amount < 0.0):
                return False
            self.sender.verify(self.signature, json_string.encode('utf-8'))
            return True
        except(ecdsa.keys.BadSignatureError):
            return False

    def __eq__(self, otherTransaction: 'Transaction'):
        # Check whether transactions are the same
        if(self.to_json() == otherTransaction.to_json() and
            self.signature != None):
            return True
        return False

if __name__ == "__main__":

    newtransaction = Transaction(vk, vk2, 123.1, sender_key=sk)
    assert(newtransaction.validate())
    # Tests if validation works

    newtransaction2 = Transaction(vk2, vk, 3.1, signature=newtransaction.signature)
    assert(not newtransaction2.validate())
    # Tests if validation works for wrong signatures.

    newtransaction5 = Transaction(vk, vk2, 123.1)
    assert(not newtransaction5.validate())
    # Tests if validation works without signature

    x = newtransaction.to_json()
    print(x)
    # Tests if to_json() gives a nice json

    newtransaction4 = Transaction.from_json(x)
    assert(newtransaction4.validate())
    # Tests if from_json works.

    newtransaction3 = Transaction(vk, vk2, 123.1, signature=newtransaction.signature)
    assert(newtransaction4 == newtransaction3)
    # Testing both __eq__() and whether from_json() works correctly.

    assert not (newtransaction3 == newtransaction2)
    # Tests if __eq__() can fail.

    newtransaction2.signature = newtransaction2.sign(sk2)
    assert(newtransaction2.validate())
    # Tests if signature can be overwritten with correct signature/tests sign()

    print('end')