import transaction
import re
import wallet

def validation(tx):
    if tx == None:
        print('Invalid transaction')
        return
    try:
        check_address(tx.sender)
        check_address(tx.recipient)
        check_sender_address(tx.sender, tx.public_key)
        check_validity(tx)
    except Exception as msg:
        print(str(msg))
        return False
    return True
    
def check_address(address):
    assert len(address) >= 25 and len(address) <= 34, "Invalid address length." + str(len(str(address)))
    assert address[0] == '1', "The address must always starts with a 1."
    
    assert str.isalnum(address) and re.findall('[0OIl]', address) == [], "An address can contain all alphanumeric characters, with the exceptions of 0, O, I, and l."
    return True
    

def check_sender_address(address, public_key):
    assert wallet.pubToAddress(public_key) == address, "Invalid sender address."
    
def check_validity(trn):
    assert wallet.sign_verify(trn.signed_hash, trn.public_key, trn.calculate_hash()), "Invalid digital signature of transaction."
    
def check_coinbase(tx):
    try:
        assert tx.sender == "0" * 34, 'Invalid coinbase transaction'
        check_address(tx.recipient)
        check_sender_address(tx.recipient, tx.public_key)
        check_validity(tx)
    except Exception as msg:
        print(str(msg))
        return False
    return True
    