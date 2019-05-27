import time
import json
import transaction
import blockchain
import block
import pending_pool
import blockchain
import cmd, sys
from config import URL, NODE_PORT
from miner_config import MINER_ADDRESS, PRIVATE_KEY
import serializer


class MinerCli(cmd.Cmd):
    intro = "Welcome miner. Thank you for your work! :) \nType help or ? to list commands. \n   "
    prompt = '(miner-cli)'
    def __init__(self, port = NODE_PORT):
        self.gblockchain = None
        try:
            self.gblockchain = blockchain.Blockchain(URL, port)

        except Exception as msg:
            print(str(msg))
            sys.exit()
        super(MinerCli, self).__init__()
            
        
    def do_mine(self, arg):
        """майнит до тих пор, пока не смайнит первым один один блок"""
        if MINER_ADDRESS == None or PRIVATE_KEY == None:
            print('For mining you should have the public_address and private_key.wif correct files')
            return
        
        coinbase = transaction.CoinbaseTransaction(MINER_ADDRESS)
        coinbase.sign(PRIVATE_KEY)
        coinbase = serializer.Serializer.serialize(coinbase)
        if self.gblockchain.BLOCKCHAIN == []:
            b = self.gblockchain.genesis_block(coinbase)
            self.gblockchain.mine(b)
            return
        else:
            try:
                """[TODO] Брать транзакции через api"""
                txs = pending_pool.take_transactions()
            except Exception as msg:
                print(msg)
                return
            txs.insert(0, coinbase)
            b = block.Block(time.time(), self.gblockchain.BLOCKCHAIN[-1].hash, txs)
        if b.validate_transactions():
            self.gblockchain.mine(b)
            #self.do_mine(None)
    
    def do_add_node(self, arg):
        """вызывает метод с класа блокчейн"""
        arg = arg.replace(' ', '')
        self.gblockchain.add_node(arg)
    
    def do_consensus(self, arg):
        self.gblockchain.resolve_conflicts()


if __name__ == '__main__':
    MinerCli().cmdloop()
