import hashlib
import wallet

class Transaction:
    def __init__(self, sender, recipient, amount):
        self.sender = sender
        self.recipient = recipient
        #assert amount >= 0 and amount <= 65535, "Invalid amount of transaction. [0;65535]"
        self.amount = amount
        self.signed_hash = None
        self.public_key = None
    
    def calculate_hash(self):
        concatenation = self.sender + self.recipient + str(self.amount)
        trn_hash = hashlib.sha256(concatenation.encode('utf-8')).hexdigest()
        return trn_hash
    
    def sign(self, private_key):
        try:
            sp = wallet.digital_signature(private_key, self.calculate_hash())
            self.signed_hash = sp[0]
            self.public_key = sp[1]
        except:
            raise Exception('Invalid transaction.')
        
class CoinbaseTransaction(Transaction):
    def __init__(self, recipient):
        super(CoinbaseTransaction, self).__init__("0" * 34, recipient, 50)
