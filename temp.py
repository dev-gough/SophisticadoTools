# TODO Get eth blockchain working on server
# TODO Communicate with said chain

import os
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()

MAINNET_ENDPOINT=os.getenv('MAINNET_ENDPOINT')

w3 = Web3(Web3.HTTPProvider('http://192.168.0.12:8545'))

print(MAINNET_ENDPOINT)