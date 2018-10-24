from wallet import Wallet
from transaction import Transaction
from merkletree import verify_proof
from flask import Flask, request
from typing import List
import requests
import ecdsa
import sys
import random

app = Flask(__name__)

headers: List[str] = []
miners = []
clients = []
wallet = Wallet()
sent_transactions: List[str] = []

@app.route('/')
def homepage():
    totalstr = "<h1>SPVClient</h1><br><br>Headers: "
    totalstr += str(headers)
    totalstr += "<br>Wallet key: {}<br>".format(wallet.get_public_key().to_string().hex())
    return (totalstr)

@app.route('/info')
def infopage():
    totalstr = ""
    totalstr += "Wallet key: {}<br>".format(wallet.get_public_key().to_string().hex())
    if(len(miners) != 0):
        try:
            balance = requests.get("http://localhost:{}/check_balance/{}".format(
                random.choice(miners),
                wallet.get_public_key().to_string().hex()
            )).text
            balance = float(balance)
            totalstr += "Balance: {}".format(balance)
        except ValueError: 
            pass
    return totalstr

@app.route('/add_miner/<miner_id>')
def add_miner(miner_id):
    if(miner_id in miners):
        return "Miner already in neighbour"
    miners.append(miner_id)
    return "Added miner: {}".format(miners[-1])

# @app.route('/receive_header', methods=["POST"])
# def receive_header():
#     header = request.form["header"]
#     if(type(header) == bytes):
#         header = header.decode()
#     headers.append(header)
#     return (redirect(url_for("")))

# r => receiver
# a => amount
# c => comment
@app.route('/create_transaction')
def create_transaction():
    receiver_raw = request.args['r']
    receiver_bytes = bytes.fromhex(receiver_raw)
    receiver = ecdsa.VerifyingKey.from_string(receiver_bytes)
    amount = request.args['a']
    comment = request.args['c']
    new_transaction = Transaction(
        wallet.get_public_key(),
        receiver, 
        float(amount), 
        comment, 
        sender_key = wallet.sk
    )
    send_transaction(new_transaction.to_json())
    sent_transactions.append(new_transaction.to_json())
    return "Transaction sent: {}".format(new_transaction.to_json())

# Not working   
@app.route('/request_proof')
def requestproof():
    if(len(sent_transactions) == 0):
        return "No transactions sent"
    return request_proof(sent_transactions[-1])

# Validates the previous transaction done by this client
@app.route('/validate_transaction')
def validateproof():
    if(len(sent_transactions) == 0):
        return "No transactions sent"
    return validate_proof(sent_transactions[-1])

@app.route('/check_balance')
def check_balance():
    if(len(miners) == 0):
        return "No miners to check with, try /add_miner"
    return requests.get("http://localhost:{}/check_balance/{}".format(
        random.choice(miners),
        wallet.get_public_key().to_string().hex()
    )).text


#Sends input transaction to all miners in miners list
def send_transaction(transaction_json: str):
    data = {"transaction": transaction_json}
    for miner_port in miners[:]:
        try:
            url = "http://localhost:{}/receive_transaction".format(miner_port)
            requests.post(url, data)
        except:
            print("Connection error for miner: {}".format(miner_port))



# Requests proof from a random miner in miners.
def request_proof(transaction_json: str):
    if(len(miners) < 1):
        return "Need miners"
    url = "http://localhost:{}/request_proof".format(random.choice(miners))
    data = {"transaction": transaction_json}
    proof_str = requests.post(url,data).json()
    proof = proof_str[0]
    root = bytes.fromhex(proof_str[1])
    result = verify_proof(transaction_json.encode(), proof, root )
    return "{}<br>{}".format(proof_str, str(result))
    

# Validates proof from a random miner.    
def validate_proof(transaction_json: str):
    if(len(miners) < 1):
        return "Need miners"
    url = "http://localhost:{}/validate_proof".format(random.choice(miners))
    data = {"transaction": transaction_json}
    proof = requests.post(url,data).text
    if(proof == "1"):
        return "True"
    return "False"



if __name__ == '__main__':
    port = sys.argv[1]
    clients.append(port)
    app.run(port=int(port))