import hashlib
import wallet
import struct
import base58
import binascii
import hashlib
import ecdsa
import codecs

class Transaction:
    def __init__(self, sender, recipient, amount):
        self.sender = sender
        self.recipient = recipient
        #assert amount >= 0 and amount <= 65535, "Invalid amount of transaction. [0;65535]"
        self.amount = amount
        self.signed_hash = None
        self.public_key = None
        
        self.version = struct.pack("<L", 1)
        self.tx_in_count = struct.pack("<B", 1)
        self.tx_in = {}
        self.tx_out_count = struct.pack('<B', 2)
        self.tx_out1 = {}
        self.tx_out2 = {}
        self.lock_time = struct.pack("<L", 0)
        
    
    def flip_byte_order(self, string):
        flipped = "".join(reversed([string[i : i + 2] for i in range(0, len(string), 2)]))
        return flipped
    
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


        
outpoint = "0338514c922d6d0b2970cad1901a87d500234423a1e5bf9a0e9de0ec33e4485311"
            
Charlie_addr		= "2N9eJQvUF3FCynYKvtVwY2ig3WQb8qCryaT"

Bob_addr		= "2N85t9wBbV9365ZbG23iJ5n3FAiQX9HmrT2"  #iam

bob_hashed_pubkey = base58.b58decode(Bob_addr[1:]).hex()

charlie_hashed_pubkey = base58.b58decode(Charlie_addr[1:]).hex()

t = Transaction('1NWzVg38ggPoVGAG2VWt6ktdWMaV6S1pJK', '1ANRQ9bEJZcwXiw7YZ6uE5egrE7t9gCyip', 12)
t.tx_in["txouthash"] = binascii.unhexlify(t.flip_byte_order(outpoint))
#print(t.tx_in['txouthash'])
t.tx_in["tx_out_index"] = struct.pack("<L", 0)
t.tx_in["script"] = binascii.unhexlify(("76a914%s88ac" % bob_hashed_pubkey))
t.tx_in["script_bytes"] = struct.pack("<B", len(t.tx_in["script"]))
t.tx_in["sequence"] = binascii.unhexlify("ffffffff")


t.tx_out1['value'] = struct.pack('<Q', 10539865)
t.tx_out1['pk_script'] = binascii.unhexlify(("76a914%s88ac" % charlie_hashed_pubkey))
t.tx_out1['pk_script_bytes'] = struct.pack('<B', len(t.tx_out1['pk_script']))

t.tx_out2['value'] = struct.pack('<Q', 10000000)
t.tx_out2['pk_script'] = binascii.unhexlify(("76a914%s88ac" % bob_hashed_pubkey))
t.tx_out2['pk_script_bytes'] = struct.pack('<B', len(t.tx_out2['pk_script']))
#t.flip_byte_order(outpoint)

raw_tx_string = (
    t.version
    + t.tx_in_count
    + t.tx_in['txouthash']
    + t.tx_in['tx_out_index']
    + t.tx_in['script_bytes']
    + t.tx_in['script']
    + t.tx_in['sequence']
    + t.tx_out_count
    + t.tx_out1['value']
    + t.tx_out1['pk_script_bytes']
    + t.tx_out1['pk_script']
    + t.tx_out2['value']
    + t.tx_out2['pk_script_bytes']
    + t.tx_out2['pk_script']
    + t.lock_time
    + struct.pack('<L', 1)
)

hashed_tx_to_sign = hashlib.sha256(hashlib.sha256(raw_tx_string).digest()).digest()

bob_private_key = wallet.wifToPriv('cTrQ7BinT9X5FPnZi6cwQXBs6THeDoGrtYJN2s9Com3AKqWSGR8z')
bob_private_key = t.flip_byte_order(bob_private_key)[2:]
#print(bob_private_key)

sk = ecdsa.SigningKey.from_string(codecs.decode(bob_private_key, 'hex') , curve = ecdsa.SECP256k1)

vk = sk.verifying_key

public_key = binascii.hexlify(b'\04' + vk.to_string())
signature = sk.sign_digest(hashed_tx_to_sign, sigencode = ecdsa.util.sigencode_der)

sigscript = (
    signature 
    + b'\01'
    + struct.pack('<B', len(public_key))
    + public_key
)


real_tx = (
    t.version
    + t.tx_in_count
    + t.tx_in['txouthash']
    + t.tx_in['tx_out_index']
    + struct.pack('<B', len(sigscript) + 1)
    + struct.pack('<B', len(signature) + 1)
    + sigscript
    + t.tx_in['sequence']
    + t.tx_out_count
    + t.tx_out1['value']
    + t.tx_out1['pk_script_bytes']
    + t.tx_out1['pk_script']
    + t.tx_out2['value']
    + t.tx_out2['pk_script_bytes']
    + t.tx_out2['pk_script']
    + t.lock_time
    + struct.pack('<L', 1)
)

print(binascii.hexlify(real_tx).decode('utf-8'))