import time
import block
import json
from flask import Flask
from flask import request
import tx_validator
import requests
import initializer as system
import block_validator

class Blockchain:
    
    def __init__(self, URL, NODE_PORT):
        self.URL = URL
        self.NODE_PORT = str(NODE_PORT)
        self.complexity = 2
        
        self.BLOCKCHAIN = []
        self.NODES = []
        #print(NODE_PORT)
        self.get_friendly_nodes()
        self.NODE_PENDING_TRANSACTIONS = []
        self.get_my_chain()
        
        
    def mine(self, block):
        if block.mine(self.complexity):
            if self.resolve_conflicts() == False:
                """нужно вернуть транзакции в пул"""
                return
            self.BLOCKCHAIN.append(block)
            requests.post(self.URL + self.NODE_PORT + '/newblock', json = system.obj_to_dictionary(block))
            print(block.hash)
            return True
        else:
            self.resolve_conflicts()
            return False
    
    def get_my_chain(self):
        try:
            new_chain = requests.get(self.URL + self.NODE_PORT + '/chain').content
            d = json.loads(new_chain.decode('utf-8'))
            new = system.dictionary_to_list(d)
            f = new.copy()
            self.BLOCKCHAIN = new
        except:
            raise Exception('Please, run the server. Use command: python3 initializer.py.')
        try:
            if self.BLOCKCHAIN != []:
                self.is_valid_chain(self.BLOCKCHAIN)
            self.resolve_conflicts()
        except Exception as msg:
            print(str(msg))
            
            
    def get_friendly_nodes(self):
        nds = requests.get(self.URL + self.NODE_PORT + '/nodes').content
        dct = json.loads(nds.decode('utf-8'))
        
        for i in dct:
            self.NODES.append(i)
        if self.NODES == []:
            print("You don't have friendly nodes.")
    
    def resolve_conflicts(self):
        longest_chain_node = None
        longest_chain_length = 0
        d = None
        for node in self.NODES:
            try:
                d = requests.get(self.URL + node + '/chain/length').json()
            except:
                print('\nNode with port ' + node + ' is inactive.')
                continue
            node_chain_length = d['length']
            if  node_chain_length > longest_chain_length:
                longest_chain_node = node
                longest_chain_length = node_chain_length
                
        d = requests.get(self.URL + self.NODE_PORT + '/chain/length').json()
        my_length = d['length']
        
        print("\nPort of node with longest chain: " + str(longest_chain_node))
        print("Longest peer node chain: " + str(longest_chain_length))
        print("Length of your chain: " + str(my_length), end='\n\n')
        
        if (longest_chain_length > my_length):
            new_chain = requests.get(self.URL + longest_chain_node + '/chain').content
            d = json.loads(new_chain.decode('utf-8'))
            new = system.dictionary_to_list(d)
            f = new.copy()
            try:
                self.is_valid_chain(f)
            except Exception as msg:
                print(str(msg))
                '''тут удаление ноды с невалидным блокчейном'''
                '''тут вызов resolve_conflicts еще раз'''
                return
            count_conflict_blocks = 0
            while count_conflict_blocks < len(self.BLOCKCHAIN):
                if self.BLOCKCHAIN[count_conflict_blocks].hash != new[count_conflict_blocks].hash:
                    break
                count_conflict_blocks = count_conflict_blocks + 1
            self.BLOCKCHAIN = new
            self.write_chain(count_conflict_blocks)
            print('Conflicts resolved. Your blockchain is updated')
            print("Length of your chain: " + str(len(self.BLOCKCHAIN)), end='\n\n')
            return False
        print('No conflicts.')
        return True

    def write_chain(self, start_id):
        i = start_id
        while i < len(self.BLOCKCHAIN):
            requests.post(self.URL + self.NODE_PORT + '/newblock', json = system.obj_to_dictionary(self.BLOCKCHAIN[i]))
            i = i + 1
        
    def is_valid_chain(self, chain):
        prev = block.Block('1', '1', '1')
        prev.hash = '0' * 64
        for b in chain:
            block_validator.validate(b)
            if prev != None:  
                assert prev.hash == b.previous_hash, "Invalid blockchain!"
            prev = b
        return True
            
        
    def add_node(self, node):
        nd = {'port' : node}
        requests.post(self.URL + self.NODE_PORT + '/addnode', json = nd)
        print('Node with port ' + node + ' added.')
            
        
    def genesis_block(self, coinbase):
        gb = block.Block(str(time.time()), '0' * 64, coinbase)
        return gb
        
    def tostr(self):
        print('#' * 100)
        for nd in self.BLOCKCHAIN:
            print(nd.previous_hash, end="")
            print(' -> ', end="")
            print(nd.hash)
        print('#' * 100)