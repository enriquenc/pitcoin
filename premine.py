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
import miner_cli

from config import URL, NODE_PORT

def premine():
    kg = wallet.KeyGenerator()
    priv_keys = []
    addresses = []
    f_addr = open('public_address', 'w+')
    f_privk = open('private_key.wif', "w+")
    for i in range(3):
        priv_keys.append(kg.generate_key())
        addresses.append(wallet.pubToAddress(wallet.privToPub(priv_keys[i])))
        f_privk.write(wallet.privToWif(priv_keys[i]) + '\n')
        f_addr.write(addresses[i] + '\n')
    
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
        
        
premine()