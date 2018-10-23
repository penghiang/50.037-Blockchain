from SPVClient import SPVClient
from flask import Flask, request, redirect, url_for
from typing import List
import requests

app = Flask(__name__)
headers: List[str] = []



@app.route('/')
def homepage():
    totalstr = "<h1>SPVClient</h1>\nHeaders: "
    totalstr += str(headers)
    return (totalstr)

@app.route('/receive_header', methods=["POST"])
def receive_header():
    header = request.form["header"]
    if(type(header) == bytes):
        header = header.decode()
    headers.append(header)
    return (redirect(url_for("")))



if __name__ == '__main__':
    app.run(port=5100)
    client = SPVClient()