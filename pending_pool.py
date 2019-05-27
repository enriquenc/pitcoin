import serializer
import transaction
import tx_validator
import requests
import json

from config import URL, NODE_PORT

def pending_pool(serialized):
    tx = None
    try:
        tx = make_obj(serialized)
    except:
        return
    if tx_validator.validation(tx) == False:
        return 
    save_to_mempool(serialized)

def save_to_mempool(serialized):
    f = open('mempool', 'a+')
    f.write(serialized + '\n')
    f.close()

def make_obj(serialized):
    d = None
    try:
        d = serializer.Deserializer.deserialize(serialized)
    except:
        raise Exception('Invalid serialized form of transaction.')
        return
    tx = transaction.Transaction(d["sender"], d["recipient"], d["amount"])
    tx.signed_hash = d["signed_hash"]
    tx.public_key = d["public_key"]
    return tx


def take_transactions():
    pending_transactions = requests.get(URL + NODE_PORT + '/transactions/pendings').content
    pending_transactions = json.loads(pending_transactions)

    assert len(pending_transactions) > 0, "Mempool is empty"
    assert len(pending_transactions) >= 3, "No 3 transactions in mempool"
    return (pending_transactions[-3:])
