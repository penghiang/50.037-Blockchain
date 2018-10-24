from miner import Miner, Block, Transaction
from flask import Flask, request
import ecdsa
import requests
import sys
import json

app = Flask(__name__)
miners = []
clients = []
buffer = []


miner = Miner()

@app.route('/')
def homepage():
    totalstr = "<h1>Miner 1</h1>"
    return totalstr

@app.route('/info')
def infopage():
    totalstr = "<h2></h2>"
    totalstr += "Wallet key: {}<br><br>".format(miner.wallet.get_public_key().to_string().hex())
    totalstr += "Coins available: {}<br><br>".format(miner.wallet.get_amount())
    totalstr += "Neighbours: {}<br><br>".format(str(miners[1:]))
    totalstr += "Length of longest blockchain: {}<br><br>".format(
        miner.blockchain.get_longest_chain().length, 
    )
    totalstr += "Block headers: <br>"
    for blocknode in miner.blockchain.blocks:
        totalstr += blocknode.block.get_header().hex() + "<br>"
    totalstr += "<br>Balances:<br>"
    balances = miner.get_current_balance()
    for i in balances:
        totalstr += "{}: {}<br>".format(i.hex(), balances[i])
    return totalstr

@app.route('/add_miner/<miner_id>')
def add_miner(miner_id):
    if(miner_id == miners[0]):
        return "Cannot add self to miners"
    if(miner_id in miners):
        return "Miner already in neighbour"
    miners.append(miner_id)
    return "Added miner: {}".format(miners[-1])

@app.route('/add_client/<client_id>')
def add_client(client_id):
    if(client_id in clients):
        return "Client already in neighbour"
    clients.append(client_id)
    return "Added client: {}".format(clients[-1])

@app.route('/mine')
def mine():
    buffer.clear()
    prev_length = len(miner.blockchain.blocks)
    while(len(buffer) == 0):
        block = miner.mine_once()
        if(block is not None):
            send_block(block.to_json())
            return "Mined a block."

    # new_block = Block.from_json(buffer[0])
    # received = miner.receive_block(new_block)
    if(len(miner.blockchain.blocks) > prev_length):
        return "Interrupted mining, new block received."
    else:
        return "Interrupted mining, new block not received??"

@app.route('/receive_block', methods=["POST"])
def receive_block():
    new_block_json = request.form["block"]
    new_block = Block.from_json(new_block_json)
    if(miner.receive_block(new_block)):
        buffer.append(new_block_json)
        return "Block received"
    else:
        return "Bad block, not received. Might be orphan."

@app.route('/receive_transaction', methods=["POST"])
def receive_transaction():
    new_transaction_json = request.form["transaction"]
    new_transaction = Transaction.from_json(new_transaction_json)
    if(miner.add_transaction(new_transaction)):
        return "Transaction added"
    else:
        return "Failed to add transaction."
        

# r => receiver
# a => amount
# c => comment
@app.route('/create_transaction')
def create_transaction():
    receiver_raw = request.args['r']
    receiver_bytes = bytes.fromhex(receiver_raw)
    receiver = ecdsa.VerifyingKey.from_string(receiver_bytes)
    amount = request.args['a']
    try:
        comment = request.args['c']
    except KeyError:
        comment = ""
    new_transaction = Transaction(
        miner.wallet.get_public_key(),
        receiver, 
        float(amount), 
        comment, 
        sender_key = miner.wallet.sk
    )
    if(miner.add_transaction(new_transaction)):
        send_transaction(new_transaction.to_json())
        return "Transaction sent: {}".format(new_transaction.to_json())
    else:
        return "Bad transaction"

# Not working
@app.route('/request_proof', methods=["POST"])
def provide_proof() -> str:
    transaction_json = request.form["transaction"]
    transaction = Transaction.from_json(transaction_json)
    proof, root = miner.verify_transaction(transaction)
    if(proof is not None):
        return json.dumps([proof, root.hex()])
    return ""

@app.route('/check_balance/<key>')
def check_balance(key: str):
    current_balance = miner.get_current_balance()
    return str(current_balance[bytes.fromhex(key)])

@app.route('/validate_proof', methods=["POST"])
def validate_proof() -> str:
    transaction_json = request.form["transaction"]
    transaction = Transaction.from_json(transaction_json)
    proof = miner.verify_transaction(transaction)
    if(proof):
        return "1"
    return ""



# Sends input block to all miners in miners list
def send_block(block_json: str):
    data = {"block": block_json}
    for miner_port in miners[1:]:
        try:
            url = "http://localhost:{}/receive_block".format(miner_port)
            requests.post(url, data)
        except:
            print("Connection error for miner: {}".format(miner_port))


#Sends input transaction to all miners in miners list
def send_transaction(transaction_json: str):
    data = {"transaction": transaction_json}
    for miner_port in miners[1:]:
        try:
            url = "http://localhost:{}/receive_transaction".format(miner_port)
            requests.post(url, data)
        except:
            print("Connection error for miner: {}".format(miner_port))


if __name__ == '__main__':
    port = sys.argv[1]
    miners.append(port)
    app.run(port=int(port))