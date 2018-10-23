from miner import Miner, Block
from flask import Flask, request
import requests
import sys

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
    totalstr += "Neighbours: {}<br><br>".format(str(miners[1:]))
    totalstr += "Length of blockchain: {}<br><br>Coins available: {}<br><br>".format(
        len(miner.blockchain.blocks), 
        miner.wallet.get_amount()
    )
    totalstr += "Block headers: <br>"
    for blocknode in miner.blockchain.blocks:
        totalstr += blocknode.block.get_header().hex() + "<br>"
    totalstr += "<br>Balances:<br>"
    balances = miner.get_current_balance()
    for i in balances:
        totalstr += "{}: {}<br>".format(i, balances[i])
    return totalstr

@app.route('/add_miner/<miner_id>')
def add_miner(miner_id):
    if(miner_id == miners[0]):
        return "Cannot add self to miners"
    miners.append(miner_id)
    return "Added miner: {}".format(miners[-1])

@app.route('/add_client/<client_id>')
def add_client(client_id):
    clients.append(client_id)
    return "Added client: {}".format(clients[-1])

@app.route('/mine')
def mine():
    while(len(buffer) == 0):
        block = miner.mine_once()
        if(block is not None):
            send_block(block.to_json())
            return "Mined a block."

    new_block = Block.from_json(buffer[0])
    received = miner.receive_block(new_block)
    buffer.pop(0)
    if(received):
        return "Interrupted mining, new block received."
    else:
        return "Interrupted mining, new block bad."

@app.route('/receive_block', methods=["POST"])
def receive_block():
    new_block_json = request.form["block"]
    new_block = Block.from_json(new_block_json)
    if(miner.receive_block(new_block)):
        buffer.append(new_block_json)
        return "Block received"
    else:
        return "Bad block, not received."
        

# Sends input block to all miners in miners list
def send_block(block_json: str):
    data = {"block": block_json}
    for miner_port in miners[1:]:
        try:
            url = "http://localhost:{}/receive_block".format(miner_port)
            requests.post(url, data)
        except:
            print("Connection error for url: {}".format(miner_port))


if __name__ == '__main__':
    port = sys.argv[1]
    miners.append(port)
    app.run(port=int(port))