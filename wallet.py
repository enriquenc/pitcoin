import time
import random
import secrets
import hashlib
import base58
import codecs
import ecdsa
import binascii
import utils

class KeyGenerator:
    def __init__(self):
        self.POOL_SIZE = 256
        self.KEY_BYTES = 32
        self.CURVE_ORDER = int('FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141', 16)
        self.pool = [0] * self.POOL_SIZE
        self.pool_pointer = 0
        self.prng_state = None
        self.__init_pool()
        
    def seed_input(self, str_input):
        time_int = int(time.time())
        self.__seed_int(time_int)
        for char in str_input:
            char_code = ord(char)
            self.__seed_byte(char_code)
            
    def generate_key(self):
        big_int = self.__generate_big_int()
        big_int = big_int % (self.CURVE_ORDER - 1) 
        big_int = big_int + 1 
        key = hex(big_int)[2:]
        key = key.zfill(self.KEY_BYTES * 2)
        return key

    def __init_pool(self):
        for i in range(self.POOL_SIZE):
            random_byte = secrets.randbits(8)
            self.__seed_byte(random_byte)
        time_int = int(time.time())
        self.__seed_int(time_int)

    def __seed_int(self, n):
        self.__seed_byte(n)
        self.__seed_byte(n >> 8)
        self.__seed_byte(n >> 16)
        self.__seed_byte(n >> 24)

    def __seed_byte(self, n):
        self.pool[self.pool_pointer] ^= n & 255
        self.pool_pointer += 1
        if self.pool_pointer >= self.POOL_SIZE:
            self.pool_pointer = 0
    
    def __generate_big_int(self):
        if self.prng_state is None:
            seed = int.from_bytes(self.pool, byteorder='big', signed=False)
            random.seed(seed)
            self.prng_state = random.getstate()
        random.setstate(self.prng_state)
        big_int = random.getrandbits(self.KEY_BYTES * 8)
        self.prng_state = random.getstate()
        return big_int
    
def privToWif(private_key):
    versioned_key = "80" + private_key
    priv_hash_1 = hashlib.sha256(binascii.unhexlify(versioned_key)).hexdigest()
    priv_hash_2 = hashlib.sha256(binascii.unhexlify(priv_hash_1)).hexdigest()
    binary_data = versioned_key + str(priv_hash_2)[:8]
    wif = base58.b58encode(binascii.unhexlify(binary_data))
    return wif.decode('utf-8')

def wifToPriv(wif):
    binary_data = base58.b58decode(wif)
    hex_data = binascii.hexlify(binary_data)
    check_sum = hex_data[-8:]
    versioned_key = hex_data[0:-8]
    priv_hash_1 = hashlib.sha256(binascii.unhexlify(versioned_key)).hexdigest()
    priv_hash_2 = hashlib.sha256(binascii.unhexlify(priv_hash_1)).hexdigest()
    check_sum_of_hash = str(priv_hash_2)[0:8].encode('utf-8')
    assert check_sum == check_sum_of_hash , "Houston we've got a problem with WIF key"
    private_key = versioned_key[2:]
    return private_key.decode('utf-8')

def privToPub(private_key):
    priv_key_bytes = codecs.decode(private_key, 'hex')
    key = ecdsa.SigningKey.from_string(priv_key_bytes, curve=ecdsa.SECP256k1).verifying_key
    key_bytes = key.to_string()
    key_hex = codecs.encode(key_bytes, 'hex')
    btc_byte = b'04'
    public_key = btc_byte + key_hex
    return public_key.decode('utf-8')

def pubToAddress(public_key):
    sha256_bpk = hashlib.sha256(public_key.encode('utf-8'))
    sha256_bpk_digest = sha256_bpk.digest()
    ripemd160_bpk = hashlib.new('ripemd160')
    ripemd160_bpk.update(sha256_bpk_digest)
    ripemd160_bpk_digest = ripemd160_bpk.digest()
    ripemd160_bpk_hex = codecs.encode(ripemd160_bpk_digest, 'hex')
    network_byte = b'00'
    network_bitcoin_public_key = network_byte + ripemd160_bpk_hex
    network_bitcoin_public_key_bytes = codecs.decode(network_bitcoin_public_key, 'hex')
    sha256_nbpk = hashlib.sha256(network_bitcoin_public_key_bytes)
    sha256_nbpk_digest = sha256_nbpk.digest()
    sha256_2_nbpk = hashlib.sha256(sha256_nbpk_digest)
    sha256_2_nbpk_digest = sha256_2_nbpk.digest()
    sha256_2_hex = codecs.encode(sha256_2_nbpk_digest, 'hex')
    checksum = sha256_2_hex[:8]
    address_hex = (network_bitcoin_public_key + checksum).decode('utf-8')
    address = base_58(address_hex)
    return address

def base_58(address_hex):
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    b58_string = ''
    leading_zeros = len(address_hex) - len(address_hex.lstrip('0'))
    address_int = int(address_hex, 16)
    while address_int > 0:
        digit = address_int % 58
        digit_char = alphabet[digit]
        b58_string = digit_char + b58_string
        address_int //= 58
    ones = leading_zeros // 2
    for one in range(ones):
        b58_string = '1' + b58_string
    return b58_string

def digital_signature(private_key, message):
    private_key_bytes = codecs.decode(private_key, 'hex')
    sk = ecdsa.SigningKey.from_string(private_key_bytes, curve = ecdsa.SECP256k1)
    signed_msg = sk.sign(message.encode('utf-8'))
    return (signed_msg.hex(), privToPub(private_key))


def sign_verify(signed_message, public_key, message):
    vk = ecdsa.VerifyingKey.from_string(bytes.fromhex(public_key[2:]), curve=ecdsa.SECP256k1)
    try:
        vk.verify(bytes.fromhex(signed_message), message.encode('utf-8'))
    except:
        return False
    return True