import wallet
import tx_validator

MINER_ADDRESS = None
try:
    f = open('public_address', 'r')
    MINER_ADDRESS = f.readline()[:-1]
    tx_validator.check_address(MINER_ADDRESS)
    f.close()
except:
    print('No public_address file or address is invalid. Please create it for creating coinbase transactions.(Use wallet-cli)')
    
PRIVATE_KEY = None

try:
    f = open('private_key.wif', 'r')
    wif = f.readline()[:-1]
    #print(wif)
    PRIVATE_KEY = wallet.wifToPriv(wif)
except:
    print('No private_key.wif file or key has invalid format. Please create it for signin coinbase transactions.(Use wallet-cli)')
