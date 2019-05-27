import time
import json
from flask import Flask
from flask import request
from multiprocessing import Process, Pipe
import blockchain
import block
import tx_validator
import requests
import pending_pool
import block_validator
import sys
import wallet
import transaction
import serializer
#import miner_cli

from config import URL, NODE_PORT

node = Flask(__name__)

BLOCKCHAIN = []
NODES = []

"""служебные функции"""

def to_object(data):
    b = block.Block(data['timestamp'], data['previous_hash'], 
                          data['transactions'])
    b.hash = data['hash']
    b.nonce = data['nonce']
    b.merkle_root = data['merkle_root']
    b.complexity = data['complexity']
    return b

def to_dictionary(blckchain):
    dct = []
    d = blckchain.copy()
    for blck in d:
        dct.append({
            'timestamp' : blck.timestamp,
            'nonce' : blck.nonce,
            'previous_hash' : blck.previous_hash,
            'transactions' : blck.transactions,
            'merkle_root' : blck.merkle_root,
            'hash' : blck.hash,
            'complexity' : blck.complexity
        })
        
    return dct

def dictionary_to_list(dct):
    lst = []
    b = None
    for blck in dct:
        b = block.Block(blck['timestamp'], blck['previous_hash'], blck['transactions'])
        b.nonce = blck['nonce']
        b.merkle_root = blck['merkle_root']
        b.hash = blck['hash']
        b.complexity = blck['complexity']
        lst.append(b)
    return lst

def load_chain(blckchn):
    try:
        i = 0
        b = None
        while True:
            with open('blocks/' + '%04d' % i + '.block') as json_file:  
                data = json.load(json_file)
            b = to_object(data)
            blckchn.append(b)
            json_file.close()
            i = i + 1
    except:
        pass
    return blckchn

def obj_to_dictionary(blck):
    
    d = {
        'timestamp' : blck.timestamp,
        'nonce' : blck.nonce,
        'previous_hash' : blck.previous_hash,
        'transactions' : blck.transactions,
        'merkle_root' : blck.merkle_root,
        'hash' : blck.hash,
        'complexity' : blck.complexity
    }
    return d


"""api функции"""


@node.route('/utxo')
def utxo():
    "[TODO] Return utxo list"
    return

@node.route('/newblock', methods=['POST'])
def new_block():
    global BLOCKCHAIN
    if request.method == 'POST':
        b = request.get_json()
        #d = json.loads(b.decode('utf-8'))
        blck = to_object(b)
        if block_validator.validate(blck):
            BLOCKCHAIN.append(blck)
        "[TODO] Remove transactions from mempool"
        "[TODO] Remove spended utxo and added new"
        
        with open('blocks/' + '%04d' % int(BLOCKCHAIN.index(blck)) + '.block', 'w') as outfile:
                json.dump(b, outfile)
        return 'Added'

@node.route('/addnode',methods=['POST'])
def add_node():
    if request.method == 'POST':
        port = request.get_json()['port']
        f = open('nodes.config', 'a+')
        f.write(port + '\n')
        f.close() 
    return 'True'

@node.route('/transactions/new', methods=['POST'])
def submit_tx():
    "[TODO] send to all nodes"
    if request.method == 'POST': 
        pending_pool.pending_pool(request.get_json()['serialized'])
    return 'okay'

@node.route('/transactions/pendings')
def pending_thxs():
    f = open('mempool', 'r')
    txs = f.readlines()
    t = []
    for i in txs:
        t.append(i[:-1])
    f.close()
    return json.dumps(t)


@node.route('/chain')
def chain():
    global BLOCKCHAIN
    BLOCKCHAIN = []
    BLOCKCHAIN = load_chain(BLOCKCHAIN)
    return json.dumps(to_dictionary(BLOCKCHAIN))

@node.route('/chain/length')
def chain_length():
    global BLOCKCHAIN
    BLOCKCHAIN = []
    load_chain(BLOCKCHAIN)
    length = {'length' : len(BLOCKCHAIN)}
    length = json.dumps(length)
    return (length)
    
@node.route('/nodes')
def nodes():
    f = open('nodes.config', 'r')
    nodes = f.readlines()
    f.close()
    for i in range(len(nodes)):
        nodes[i] = nodes[i][:-1]
    return json.dumps(nodes)


@node.route('/block/', methods=['GET'])
def get_n_block():
    global BLOCKCHAIN
    BLOCKCHAIN = []
    BLOCKCHAIN = load_chain(BLOCKCHAIN)
    height = int(request.args.get('height'))
    
    print(height)
    print(len(BLOCKCHAIN))
    if height >= len(BLOCKCHAIN):
        d = {}
        return json.dumps(d)
    else:
        json_block = json.dumps(obj_to_dictionary(BLOCKCHAIN[height]))
        return json_block

@node.route('/block/last')
def get_last_block():
    global BLOCKCHAIN
    BLOCKCHAIN = []
    BLOCKCHAIN = load_chain(BLOCKCHAIN)
    return json.dumps(obj_to_dictionary(BLOCKCHAIN[-1]))

@node.route('/balance')
def get_balance():
    global BLOCKCHAIN
    BLOCKCHAIN = []
    BLOCKCHAIN = load_chain(BLOCKCHAIN)
    addr = str(request.args.get('addr'))
    balance = 0
    for b in BLOCKCHAIN :
            if BLOCKCHAIN.index(b) == 0:
                tx = pending_pool.make_obj(b.transactions)
                if tx.sender == addr:
                    balance = balance - tx.amount
                elif tx.recipient == addr:
                    balance = balance + tx.amount
            else:
                for t in b.transactions:
                    #print(t)
                    tx = pending_pool.make_obj(t)
                    if tx.sender == addr:
                        balance = balance - int(tx.amount)
                    elif tx.recipient == addr:
                        balance = balance + int(tx.amount)
    return json.dumps(balance)
    
def premine():
    kg = wallet.KeyGenerator()
    priv_keys = []
    addresses = []
    f_addr = open('public_address', 'w+')
    f_privk = open('private_key.wif', "w+")
    for i in range(3):
        priv_keys.append(kg.generate_key())
        addresses.append(wallet.pubToAddress(wallet.privToPub(priv_keys[i])))
        f_addr.write(wallet.privToWif(priv_keys[i]) + '\n')
        f_privk.write(addresses[i] + '\n')
    
    for i in range(10):
        t = transaction.Transaction(addresses[0], addresses[1], 10 + i)
        t.sign(priv_keys[0])
        tx_validator.validation(t)
        tx = {'serialized' : serializer.Serializer.serialize(t)}
        requests.post(URL + NODE_PORT + '/transactions/new', json = tx)
        
        t = transaction.Transaction(addresses[1], addresses[2], 11 + i)
        t.sign(priv_keys[1])
        tx_validator.validation(t)
        tx = {'serialized' : serializer.Serializer.serialize(t)}
        requests.post(URL + NODE_PORT + '/transactions/new', json = tx)
        
        t = transaction.Transaction(addresses[2], addresses[0], 12 + i)
        t.sign(priv_keys[2])
        tx_validator.validation(t)
        tx = {'serialized' : serializer.Serializer.serialize(t)}
        requests.post(URL + NODE_PORT + '/transactions/new', json = tx)
    
    miner = miner_cli.MinerCli(NODE_PORT)
    miner.do_mine(None)
    for i in range(10):
        miner.do_mine(None)
    
if __name__ == '__main__':
    
    p2 = Process(target = node.run(port = NODE_PORT))
    p2.start()
    #if len(sys.argv) > 1:
    #    if sys.argv[1] == '-premine':
    #        premine()
