#crypto currency
import datetime
import hashlib
import json
from flask import Flask, jsonify, request #connecting nodes in network we use request
import requests
from uuid import uuid4 #create an address for each node in the network
from urllib.parse import urlparse

# Building a Blockchain

class Blockchain:

    def __init__(self):
        self.chain = []
        self.transactions = []#list of transaction, contains tractions before theyre added to BC
        self.create_block(proof = 1, previous_hash = '0')
        self.nodes = set()
    
    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash,
                 'transactions': self.transactions}#all the transaction contained in transactionlist
        self.transactions = []#emptying list, you cannot have same transaction in 2 diff blocks
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]

    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof
    
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True
    
    def add_transaction(self, sender, receiver, amount): #method to record sender receiver and amount
        self.transactions.append({'sender': sender,    
                                  'receiver': receiver,
                                  'amount': amount})
        previous_block = self.get_previous_block() #getting previous block
        return previous_block['index'] + 1 #index of the new block which will welcome these transaction
    
    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
        
#tackle conses prob by recreating replace chain method 
    def replace_chain(self): #will replace any chain which is shorter than longest chain in node
        network = self.nodes #network  contaning all the nodes
        longest_chain = None #we dont know which is the longest chain
        max_length = len(self.chain) #to find the longest chain in the network  
        for node in network:#looping on all nodes in network  
            response = requests.get(f'http://{node}/get_chain') #requesting to get the longest chain among nodes
            if response.status_code == 200: #to check if everythings OkAy
                length = response.json()['length'] # using jason function to catch key of taking length key of a dictionary which will get us length of the cahin
                chain = response.json()['chain'] #r
                if length > max_length and self.is_chain_valid(chain): #if length is larger than max length and if 
                    max_length = length #updating max length 
                    longest_chain = chain #updating longest chain, max length become chain
        if longest_chain: #if longest chain is not none
            self.chain = longest_chain #if the longest chain is not none then chain becomes longest chain
            return True 
        return False

# Mining Blockchain

# Creating a Web App
app = Flask(__name__)

# Creating an address for the node on Port 5000
node_address = str(uuid4()).replace('-', '') #for miner to get some coin
#uuid function will generate a unique address of node
# Creating a Blockchain
blockchain = Blockchain()

# Mining a new block
@app.route('/mine_block', methods = ['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transaction(sender = node_address, receiver = 'Roshan', amount = 1) #giving coin
    block = blockchain.create_block(proof, previous_hash)
    response = {'message': 'Congratulations, you just mined a block!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions': block['transactions']} #transaction 
    return jsonify(response), 200

# Getting the full Blockchain
@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200

# Checking if the Blockchain is valid
@app.route('/is_valid', methods = ['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'All good. The Blockchain is valid.'}
    else:
        response = {'message': 'We have a problem. The Blockchain is not valid.'}
    return jsonify(response), 200

# Adding a new transaction to the Blockchain
@app.route('/add_transaction', methods = ['POST']) #POST request
def add_transaction(): #new function
    json = request.get_json() #thid will get json file posted in postman
    transaction_keys = ['sender', 'receiver', 'amount'] #3 keys of transation
    if not all(key in json for key in transaction_keys): #if keys are not in json file
        return 'Some elements of the transaction are missing', 400 #bad request, malformed request syntax
    index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'])# index of block containing new trasation 
    #this transaction doesnt take keys, it takes the values of key                                                                               
    response = {'message': f'This transaction will be added to Block {index}'} #
    return jsonify(response), 201 #201 for created

# Decentralizing Blockchain

# Connecting new nodes
@app.route('/connect_node', methods = ['POST']) #post request
def connect_node():
    json = request.get_json() #going to get request of posting a new node in network
    nodes = json.get('nodes') #getting nodes
    if nodes is None: #checking if nodes are none
        return "No node", 400
    for node in nodes: 
        blockchain.add_node(node) #addind node in blockchain
    response = {'message': 'All the nodes are now connected. MyCrypto Blockchain now contains the following nodes:',
                'total_nodes': list(blockchain.nodes)}
    return jsonify(response), 201

# Replacing the chain by the longest chain if needed
@app.route('/replace_chain', methods = ['GET']) ###
def replace_chain(): 
    is_chain_replaced = blockchain.replace_chain() #boolen
    if is_chain_replaced: #if chain is replaced
        response = {'message': 'The nodes had different chains so the chain was replaced by the longest one.',
                    'new_chain': blockchain.chain}
    else: #if chain didnt get replaced
        response = {'message': 'All good. The chain is the largest one.',
                    'actual_chain': blockchain.chain}
    return jsonify(response), 200

# Running the app
app.run(host = '0.0.0.0', port = 5001)
