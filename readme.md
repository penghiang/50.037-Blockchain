# 50.037 Blockchain Technology

## To use:
We can launch minerApp.py and SPVClientApp.py, providing the port number as an argument:

`py ./minerApp.py 5000`

`py ./minerApp.py 5001`

We then add each miner by navigating to these with our browser

`localhost:5000/add_miner/5001`

`localhost:5001/add_miner/5000`

Information about the miners can be found on:

`localhost:5000/info`

The miners are then able to mine with:

`localhost:5000/mine`

`localhost:5001/mine`

The first miner who mines a block will send an interrupt signal to all the other miners it has in its neighbours list

Other miners will check and add the new block to their blockchain.

---

To add SPVClients, we use `/add_client` instead of `/add_miner`.

SPVClients are able to create transactions.

Another example:

We first start with running an SPVClient and a miner on port 5100 and 5000 respectively.

`py ./minerApp.py 5000`

`py ./SPVClientApp.py 5100`

This example is going to show:
1. Miner mines a block
2. Miner sends Client some money
3. Miner mines another block
4. Client sends miner some money
5. Miner mines another block

We mine every other step to lock the transactions into the blockchain.

`localhost:5000/mine`

`localhost:5100/info` allows us to check the wallet's key number of the client. We make use of this to create a transaction.

`localhost:5000/create_transaction?a=999999&r=[SPVClient's key]` We try to send a bad transaction and it will be rejected.

`localhost:5000/create_transaction?a=10.70&r=[SPVClient's key]` We insert SPVClient's key into this url, 
and it will generate a transaction that is automatically added when the miner later mines a block. 

> Create transaction takes the following:
> amount => a
> receiver => r
> comment => c (optional)
> To send a transaction worth 50 to receiver that has a public key of a9d7f7, we do `/create_transaction?a=50&r=a9d7f7`

`localhost:5000/mine`

`localhost:5100/add_miner/5000` 

`localhost:5100/create_transaction?a=1&r=[Miner's key]` Miner's key can be found in miner's `/info`
This transaction is broadcast to miners that are added through `/add_miner`

`localhost:5100/validate_transaction` This checks the previous transaction if it's in the blockchain. 
It is false because the miner has not mined yet.

`localhost:5000/mine`

`localhost:5100/validate_transaction`

`localhost:5000/info` We can see that all the balances are updated with the correct transactions.





## Unimplemented 
#### Transactions
* **Miner does not reject the same transaction being sent again.**
* We do not check a transaction's timestamp, we could implement checks on timestamp and repetition
* When we have a fork, we do not pick up the shorter forks' transactions
* Transactions should have orphan handling, the deposit might come later than the withdrawal
* Highlighting which transactions are bad when receiving a block with bad transactions instead of rejecting all of them.
#### Blocks
* Hashing twice instead of hashing only once
#### Miners
* Validating of blocks' timestamps
* Raising of difficulty
* Halving of reward from coinbase transaction
#### SPVClients
* Bloom filters
#### Network
* **Miners cannot join halfway, need to sync the whole blockchain.**
* Requesting orphans' parents from miners
* Request proof not working, bytes not json serializable. Can convert everything into strings instead of bytes.
* When SPVClients create transactions, they should know if the miners have accepted their transactions.
#### Others
* **Attacks**
* Custom exceptions for failed verification/validity/other errors (currently using ValueError and True/False returns)
* Actual tests and testing classes for rigorous tests
* UTXO or smart contracts or the likes

## Implemented
#### Transactions
* Transactions within a received block can be unordered, withdrawal can come before deposit.
* Transactions that are repeated in self.transactions and a new received block are removed.
#### MerkleTree
* Leaf nodes and branches are differentiated.
#### Blockchain
* Orphans are handled, we can send the next block before the previous block
* Forks are handled, we are able to keep track of the number and length of forks in the blockchain.
* Different forks have different tables of balances (different transactions are in different forks)
#### Network
* SPVClients can check their balance with miners
* SPVClients are able to check if their transactions are in the blockchain
