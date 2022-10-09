import os
import requests
import json
from dotenv import load_dotenv
from web3 import Web3
import etherscan

load_dotenv()

ES_ENDPOINT = os.getenv('ES_ENDPOINT')
ES_API_KEY = os.getenv('ES_API_KEY')
MAINNET_ENDPOINT = os.getenv('MAINNET_ENDPOINT')
w3 = Web3(Web3.HTTPProvider(MAINNET_ENDPOINT))
es = etherscan.Client(api_key=ES_API_KEY, cache_expire_after=5)

ADDRESS = ''  # address to scan

normal_txs = es.get_transactions_by_address(address=ADDRESS)
internal_txs = es.get_transactions_by_address(address=ADDRESS, tx_type='internal')
contract_txs = es.get_token_transactions(address=ADDRESS)
txs = []

for tx in normal_txs:  # reformat transaction data to make it easily usable
    if tx['is_error']:  # if tx failed don't bother listing it
        continue
    z = []  # list to store aggregated transaction data
    z.append(tx)

    hash = tx['hash']
    internal_tx = list(filter(lambda x: x['hash'] == hash, internal_txs))  # filter internal txs list to find tx with same hash
    if len(internal_tx) != 1:
        z.append(None)
        if len(internal_tx) > 1:
            raise Exception('multiple internal txs with same address, what do??')
    else:
        z.append(internal_tx[0])
    contract_tx = list(filter(lambda x: x['hash'] == hash, contract_txs))  # filter contract txs list to find tx with same hash
    if len(contract_tx) == 0:
        z.append(None)
    elif len(contract_tx) == 1:
        z.append(contract_tx[0])
    else:
        z.append(contract_tx)

    txs.append(z)

for tx in txs:
    if not tx[1] and not tx[2]:  # no internal smart contract txs, and not an erc20 tx, can also be an approve tx (how to handle??)
        if tx[0]['to'].lower() == ADDRESS.lower():
            print('received ' + str(Web3.fromWei(tx[0]['value'], 'ether').real) + ' Eth')
        elif tx[0]['from'].lower() == ADDRESS.lower():
            print('sent ' + str(Web3.fromWei(tx[0]['value'], 'ether').real) + ' Eth')

    elif not tx[1]:  # not an internal smart contract tx, so far i've only seen this happen for buying shitcoins or contract calls
        if isinstance(tx[2], list):  # if there are multiple erc20 txs, its likely not a shitcoin purchase
            print("some kind of smart contract call going on:")
            for i in tx[2]:
                token_symbol = i['token_symbol']
                token_amount = i['value'] / pow(10, i['token_decimal'])
                if i['to'].lower() == ADDRESS.lower():
                    print("\t received", str(token_amount), token_symbol, 'from', i['from'])
                elif i['from'].lower() == ADDRESS.lower():
                    print("\t sent", str(token_amount), token_symbol, 'to', i['to'])
                else:
                    print('\ttokens not sent to or from address being scanned')
                    print('\t', i)

        elif isinstance(tx[2], dict):
            if tx[2]['to'].lower() != ADDRESS.lower():
                print('probably a contract call \tHash:', tx[2]['hash'])
                continue
            eth_spent = Web3.fromWei(tx[0]['value'], 'ether').real
            token_symbol = tx[2]['token_symbol']
            token_received = tx[2]['value']/pow(10, tx[2]['token_decimal'])
            print('spent ' + str(eth_spent) + ' Eth for ' + str(token_received), token_symbol)
        else:
            raise Exception('erc20 tx list is some kinda fucked')

    elif not tx[2]:  # idk what this means
        print('internal transaction stuff. Hash: ', tx[1]['hash'])

    else:  # internal tx, and erc20 tx. I think this means sell shitcoin
        if tx[2]['from'].lower() != ADDRESS.lower() or tx[1]['to'].lower() != ADDRESS.lower():
            print('Assumed tx was selling shitcoin, addresses be fucked idk what this means')
            continue
        eth_received = Web3.fromWei(tx[1]['value'], 'ether').real
        token_symbol = tx[2]['token_symbol']
        token_sent = tx[2]['value'] / pow(10, tx[2]['token_decimal'])
        print('sold ' + str(token_sent), token_symbol + ' for ' + str(eth_received) + ' Eth')

print("penis")
# Web3.fromWei(es.get_transactions_by_address(address=ADDRESS, tx_type='internal')[0]['value'], 'ether')
# sorted(es.get_token_transactions(address=ADDRESS), key=lambda x:x['hash'])
