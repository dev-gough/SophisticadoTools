# TODO Get eth blockchain working on server
# TODO Communicate with said chain
print("devon likes big dicks")

import os
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()

MAINNET_ENDPOINT=os.getenv('MAINNET_ENDPOINT')

w3 = Web3(Web3.HTTPProvider(MAINNET_ENDPOINT))
temp = w3.eth.getBlock('latest')
print(w3.eth.getBlock('latest'))