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

===

To add SPVClients, we use /add_client instead of /add_miner.

SPVClients are able to create transactions.


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
