# Pitcoin

Simple implementation of bitcoin.
Bitcoin: A Peer-to-Peer Electronic Cash System

## Getting Started

You need python 3.6.2 and pip 19.0.1 versions

```
~>> python3 --version
Python 3.6.2
```

```
~>> pip --version
pip 19.0.1
```

### Prerequisites

First of all download my project from git repository:

```
~>> git clone https://github.com/enriquenc/xteams.git
```

Then:

```
~>> cd xteams/pitcoin
```

To install all packages you need to run this cash system use:
```
~>> pip install -r requirements.txt
```

### Using

Okay, now you can use this node.
Fitst of all run the rpc server.
```
~>> python3 initializer.py
```

Open a new terminal window and go to the curent directory.
Launch the command line interface to create you private key:
```
~>> python3 wallet_cli.py
```
Use the new command to generate a new private key and public address.
Then use privtowif to save your private key in WIF format.
This will further allow you to mine.

![ScreenShot](https://i.imgur.com/zHAWdDP.png)

Call the send command in wallet cli with two parameters - sender address
and amount (Example of bitcoin address -  15Pdb6opS18FSfnQb3KjcbEU9sAwQPxHXN).
Then broadcast transaction to the network:

![ScreenShot](https://i.imgur.com/4aBiH7F.png)

Okay, now you have two files: public_key and private_key.wif.

Open a new terminal window and go to the curent directory.
Run miner-cli to start mining.
```
~>> python3 miner_cli.py
```
To mine one block use command mine:

![ScreenShot](https://i.imgur.com/AaFDrX2.png)

Also you can run script premine.py.
In this mode, the following actions occured:
   - Generation of three key pairs, which are saved to the separate file.
    -Genesis block launching
    -Using public addresses from generated keys above, mine ten (10) blocks, that
    -will contain different transactions between these addresses.

```
~>> python3 premine.py
```


### Routes

/transaction/pendings - return pendings transactions

/chain - return all blockchain in JSON format

/chain/length - return length of blockchain

/block/last - return last block of blockchain in JSON format

/block?height=<int> - return block of given height

/balance?addr=<address> - return the balance of given address


# TestS

To run my tests for node you should to copy the directory xteams you have just cloned
and change the config.py variable NODE_PORT to 5100 and nodes.config file content to 5000.
Run this rpc server in this directory in new terminal window.
Then open new terminal, go to the xteams directory and run tests:

```
~>> python3 test.py
```

When ran all tests you will see smth like this:

![ScreenShot](https://i.imgur.com/pB3WZD2.png)


A
