# TODO Get eth blockchain working on server
# TODO Communicate with said chain

import os
import pprint
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()

MAINNET_ENDPOINT=os.getenv('MAINNET_ENDPOINT')

w3 = Web3(Web3.HTTPProvider(MAINNET_ENDPOINT))

# Gets latest block.
""" 
Block Structure:

AttributeDict({
    'baseFeePerGas' : int,
    'difficulty' : int,
    'extraData' : HexBytes,
    'gasLimit' : int,
    'gasUsed' : int,
    'hash' : HexBytes,
    'logsBloom' : HexBytes,
    'miner' : HexBytes,
    'mixHash' : HexBytes,
    'nonce' : int,
    'parentHash' : HexBytes,
    'receiptsRoot' : HexBytes,
    'sha3Uncles' : HexBytes,
    'size' : int,
    'stateRoot' : HexBytes,
    'timestamp' : int,
    'totalDifficulty' : int,
    'transactions' : List[HexBytes],
    'transactionsRoot' : HexBytes,
    'uncles' : ? (maybe list)
})
 """
# Shows getting a HexByte object to a str
tx_id = w3.eth.get_block('latest')['transactions'][0].hex()

"""
Transaction Data:

    AttributeDict({
        'accessList' : List,
        'blockHash' : HexBytes,
        'blockNumber' : int,
        'chainID' : str,
        'from' : str,
        'gas' : int,
        'hash' : HexBytes,
        'input' : str,
        'maxFeePerGas' : int,
        'maxPriorityFeePerGas' : int,
        'nonce' int,
        'r' : HexBytes,
        's' : HexBytes,
        'to' : str,
        'transactionIndex' : int,
        'type' : str,
        'v' : int,
        'value' : int
    })
"""
# Shows getting a tx from a str
tx = w3.eth.get_transaction(tx_id)
print(tx)