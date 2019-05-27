import merkle
import hashlib
import tx_validator
import serializer
import pending_pool
import time

class Block():

    def __init__(self, timestamp, previous_hash, transactions):
        self.timestamp = timestamp
        self.nonce = 0
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.merkle_root = merkle.merkle_root(transactions)
        self.hash = self.hash_block()
        self.complexity = None
        
    def hash_block(self):
        return (hashlib.sha256((str(self.timestamp) + str(self.nonce) + self.previous_hash + self.merkle_root).encode('utf-8')).hexdigest())

    def validate_transactions(self):
        try:
            if isinstance(self.transactions, list):
                for i in self.transactions:
                    if self.transactions.index(i) == 0:
                        tx_validator.check_coinbase(pending_pool.make_obj(i))
                    continue
                tx_validator.validation(pending_pool.make_obj(i))
            else:
                tx_validator.check_coinbase(pending_pool.make_obj(i))
        except Exception as msg:
            print(str(msg))
            return False
        return True

    def mine(self, complexity):
        self.complexity = complexity
        begin = '0' * complexity
        start = int(time.time())
        
        while begin != self.hash[:complexity]:
            self.nonce = self.nonce + 1
            self.hash = self.hash_block()
            ''' Для того чтобы сбрасывать регулярно майнинг
            и исправлять конфликты с другими нодами
            if int(time.time()) - start > 5:
                return False
            '''
        return True