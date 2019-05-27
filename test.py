import unittest
import time
import requests

import color_output as co
import wallet as wt
import tx_validator as tv
import transaction as tn
import serializer as s
import pending_pool as pp
import block as bk
import block_validator as bv
import miner_cli as miner

from config import URL

kg = wt.KeyGenerator()
pk = kg.generate_key()

def is_valid_chain(chain):
        prev = bk.Block('1', '1', '1')
        prev.hash = '0' * 64
        for b in chain:
            bv.validate(b)
            if prev != None:
                assert prev.hash == b.previous_hash, "Invalid blockchain!"
            prev = b
        return True

class TestAll(unittest.TestCase):
    
    
    
    def test_wif(self):
        self.assertEqual(pk, wt.wifToPriv(wt.privToWif(pk)))
    
    def test_address(self):
        self.assertTrue(tv.check_address(wt.pubToAddress(wt.privToPub(pk))))

    def test_digital_signature(self):
        message = "message"
        s = wt.digital_signature(pk, message)
        self.assertTrue(wt.sign_verify(s[0], s[1], message))
        message = "x5zz3d1x2d21x5w1dwqswqwdxqw"
        s = wt.digital_signature(pk, message)
        self.assertTrue(wt.sign_verify(s[0], s[1], message))
        
    def test_serializer(self):
        t = tn.Transaction('15Pdb6opS18FSfnQb3KjcbEU9sAwQPxHXN', '12pULxeW59imr1mWs8AjQogji8H77KD3KT', 12)
        t.sign(pk)
        signed_hash = t.signed_hash
        public_key = t.public_key
        sr = s.Serializer.serialize(t)
        tx = pp.make_obj(sr)
        self.assertEqual(tx.signed_hash, signed_hash)
        self.assertEqual(tx.public_key, public_key)
        self.assertEqual(tx.sender, '15Pdb6opS18FSfnQb3KjcbEU9sAwQPxHXN')
        self.assertEqual(tx.recipient, '12pULxeW59imr1mWs8AjQogji8H77KD3KT')
        self.assertEqual(tx.amount, 12)
        self.assertEqual(sr, s.Serializer.serialize(tx))
        
    def test_genesis_block(self):
        t = tn.CoinbaseTransaction(wt.pubToAddress(wt.privToPub(pk)))
        t.sign(pk)
        b = bk.Block('123142.124', '0' * 64, s.Serializer.serialize(t))
        b.mine(2)
        bv.validate(b)
        
    def test_blockchain(self):
        t = tn.CoinbaseTransaction(wt.pubToAddress(wt.privToPub(pk)))
        t.sign(pk)
        genesis_block = bk.Block(time.time(), '0' * 64, s.Serializer.serialize(t))
        genesis_block.mine(2)
        bv.validate(genesis_block)
        '''genesis'''
        tr = tn.Transaction(wt.pubToAddress(wt.privToPub(pk)), '12pULxeW59imr1mWs8AjQogji8H77KD3KT', 5)
        tr.sign(pk)
        sr = s.Serializer.serialize(tr)
        lst = []
        lst.append(s.Serializer.serialize(t))
        lst.append(sr)
        lst.append(sr)
        lst.append(sr)
        b1 = bk.Block(time.time(), genesis_block.hash, lst)
        b1.mine(2)
        bv.validate(b1)
        b2 = bk.Block(time.time(), b1.hash, lst)
        b2.mine(2)
        bv.validate(b2)
        chain = []
        chain.append(genesis_block)
        chain.append(b1)
        chain.append(b2)
        #b2.timestamp = "1241"
        self.assertTrue(is_valid_chain(chain))
        chain

    def test_mining_and_consensus(self):
        sr = '007b1BZRcueSjGhQiP3AM8T3vzR9GraA6GaS2r15Pdb6opS18FSfnQb3KjcbEU9sAwQPxHXN0470f4ebc941dbaca87dd9c8072e4e390c0aaa2e06e00813aadcb8a52fa3314ce4f7902feb7b1bef7acf79f8063ae7d9b611c118b3504bad488daaade06687bc2d9a6bde96d41352b179d28531c4594fe08043f6392d5a907f81ead1d871aaabe011f9fabc605f2c6f316ac3e5071bcdca7af914d0f0ccda51f0351d4921ab39c0'
        miner1_port = '5000'
        miner2_port = '5100'
        miner1 = miner.MinerCli(miner1_port)
        miner2 = miner.MinerCli(miner2_port)
        for i in range(9):
            tx = {'serialized' : sr}
            requests.post(URL + miner1_port + '/transactions/new', json = tx)
            requests.post(URL + miner2_port + '/transactions/new', json = tx)
        miner1.do_mine(None)
        miner2.do_consensus(None)
        l1 = requests.get(URL + miner1_port  + '/chain/length').json()
        l2 = requests.get(URL + miner2_port  + '/chain/length').json()
        self.assertEqual(l1['length'], l2['length'])
        miner2.do_mine(None)
        miner2.do_mine(None)
        miner2.do_mine(None)
        miner2.do_mine(None)
        miner2.do_mine(None)
        miner1.do_consensus(None)
        l1 = requests.get(URL + miner1_port  + '/chain/length').json()
        l2 = requests.get(URL + miner2_port  + '/chain/length').json()
        self.assertEqual(l1['length'], l2['length'])
        miner1.do_mine(None)
        miner1.do_mine(None)
        miner1.do_mine(None)
        miner1.do_mine(None)
        miner1.do_mine(None)
        miner2.do_consensus(None)
            
        
        
        
        
        
        
if __name__ == '__main__':
    unittest.main()