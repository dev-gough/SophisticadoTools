import os
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()

MAINNET_ENDPOINT=os.getenv('MAINNET_ENDPOINT')
w3 = Web3(Web3.HTTPProvider(MAINNET_ENDPOINT))

n = w3.eth.getBlock('latest').number


target_recipient = '0xe756F6680de0C184Ad4419616127C1753aF685eE'

txs = []
for i in range(15628397, n):
    block = w3.eth.getBlock(i)
    for j in range(len(block.transactions)):
        print(j)
        tx_recipient = w3.eth.get_transaction(block.transactions[j]).to
        if tx_recipient == target_recipient:
            txs.append(block.transactions[j])
            print(block.transactions[j])

print(txs)


