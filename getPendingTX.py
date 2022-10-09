import os
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()

MAINNET_ENDPOINT=os.getenv('MAINNET_ENDPOINT')
w3 = Web3(Web3.HTTPProvider(MAINNET_ENDPOINT))

tx_filter = w3.eth.filter('pending')

while True:
    # pending_block = w3.eth.getBlock('pending', full_transactions=True)
    # pending_transactions = pending_block['transactions']
    # print(pending_block['number'], len(pending_transactions))
    tx_filter.get_new_entries()
