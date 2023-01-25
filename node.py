# MODULE 1- Create blockchain

import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse



#Blockchain data

class Blockchain:
    def __init__(self):
        self.chain = []
        self.transactions = [] #mempool 
        self.create_block(proof = 1, prev_hash = '0') # proof is noounce
        self.nodes = set()

    def create_block(self, proof, prev_hash):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()), 
                 'proof': proof,
                 'prev_hash': prev_hash,
                 'transactions': self.transactions}
        
        self.transactions = []
        self.chain.append(block)
        return block
    
    def add_transasction(self, sender, receiver, amount):
        self.transactions.append({'sender': sender,
                                  'receiver': receiver,
                                  'amount': amount})
        prev_block = self.get_prev_block()
        return prev_block['index'] + 1
    
    def add_node(self, address):
        parsed_url = urlparse(address)
        
        self.nodes.add(parsed_url.netloc)
        
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False
        
        
    def get_prev_block(self,):
        return self.chain[-1]
    
    def proof_of_work(self, prev_proof):
        new_proof = 1 
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof ** 2 - prev_proof ** 2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                print(hash_operation)
                check_proof = True
            else:
                new_proof += 1
        return new_proof
    
    
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys= True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    #proverimo da li je proof = 0 i da li je hash prethodnog jeddnak hashu sledeceg
    def is_chain_valid(self, chain):
        for i in range(1, len(self.chain)):
            if chain[i]['prev_hash'] != self.hash(chain[i - 1]):
                return False
            
            hash_operation = hashlib.sha256(str(chain[i]['proof'] ** 2 - chain[i-1]['proof'] ** 2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            
        return True



# Node address


node_address = str(uuid4()).replace('-', '')

#Mining a blockchain

#flash web app
app = Flask(__name__)

blockchain = Blockchain()



@app.route('/mine_block', methods= ['GET'])
def mine_blockblock():
    prev_block = blockchain.get_prev_block()
    prev_proof = prev_block['proof']
    proof = blockchain.proof_of_work(prev_proof)
    prev_hash = blockchain.hash(prev_block)
    blockchain.add_transasction(sender=node_address, receiver='ivan', amount= 3)
    block = blockchain.create_block(proof, prev_hash)
    response = {'message ': "Congratulations, new block created",
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'prev_hash': block['prev_hash'],
                'transactions': block['transactions']}
    return jsonify(response), 200

#Adding new transacstions
@app.route('/add_transaction', methods = ['POST'])
def add_transacstion():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all (key in json for key in transaction_keys):
        return {'message': 'Some elements are missing'}, 400
    index = blockchain.add_transasction(json['sender'], json['receiver'], json['amount'])
    response = {'message': f'This transaction will be added to {index} block'}
    return jsonify(response), 201
        
@app.route('/get_chain', methods= ['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200

@app.route('/is_valid', methods= ['GET'])
def is_chain_valid():
    response = jsonify(blockchain.is_chain_valid())
    return response, 200

#decentralizing our currency


@app.route('/connect_node', methods = ['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    print(nodes)
    if nodes is None:
        return "No nodes", 400
    for node in nodes:
        blockchain.add_node(node)
    response = {'message': 'All nodes are now connected. Blockchain now contains nodes:',
                'total_nodes': list(blockchain.nodes)}
    return response, 201

@app.route('/replace_chain', methods = ['GET'])
def replace_chain():
    if blockchain.replace_chain():
        response = {'message': 'Chain was replaced because longer chain was found',
                    'new_chain': blockchain.chain}
    else:
        response = {'message': 'All good. This can is the longest one',
                    'actual_chain': blockchain.chain}
    return response, 200

#run app
app.run(host = '0.0.0.0', port=5001)











