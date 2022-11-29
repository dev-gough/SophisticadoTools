import os
import sys
from objects import Portfolio
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

ADDRESS = '0x17a182f1bce80f26a0644b992e85bcd619cf3ab3'  # address to scan
p = Portfolio(ADDRESS)  # portfolio obj tracking token balances

def main():
    normal_txs = es.get_transactions_by_address(address=p.address)
    internal_txs = es.get_transactions_by_address(address=p.address, tx_type='internal')
    contract_txs = es.get_token_transactions(address=p.address)
    txs = []

    # reformat transaction data to make it easily usable

    while(len(normal_txs)+len(internal_txs)+len(contract_txs)>0):
        # check block of tx so tx logs are merged in order

        z = []  # list to store aggregated transaction data
        if normal_txs:  # check if list is empty
            normal_block = normal_txs[0]['block_number']
            normal_hash = normal_txs[0]['hash']
        else:
            normal_block = sys.maxsize
            normal_hash = None
        if internal_txs:
            internal_block = internal_txs[0]['block_number']
            internal_hash = internal_txs[0]['hash']
        else:
            internal_block = sys.maxsize
            internal_hash = None
        if contract_txs:
            contract_block = contract_txs[0]['block_number']
            contract_hash = contract_txs[0]['hash']
        else:
            contract_block = sys.maxsize
            contract_hash = None

        if normal_block <= internal_block and normal_block <= contract_block:  # if next tx is a normal tx
            z.append(appendAllTx(normal_hash, normal_txs))
            if normal_hash != internal_hash:
                z.append(None)
            else:
                z.append(appendAllTx(normal_hash, internal_txs))
            if normal_hash != contract_hash:
                z.append(None)
            else:
                z.append(appendAllTx(normal_hash, contract_txs))
        elif internal_block <= normal_block and internal_block <= contract_block:  # if next tx is internal tx
            if internal_hash != normal_hash:
                z.append(None)
            else:
                z.append(appendAllTx(internal_hash, normal_txs))
            z.append(appendAllTx(internal_hash, internal_txs))
            if internal_hash != contract_hash:
                z.append(None)
            else:
                z.append(appendAllTx(internal_hash, contract_txs))
        elif contract_block <= normal_block and contract_block <= internal_block:  # if next tx is contract tx
            if contract_hash != normal_hash:
                z.append(None)
            else:
                z.append(appendAllTx(contract_hash, normal_txs))

            if contract_hash != internal_hash:
                z.append(None)
            else:
                z.append(appendAllTx(contract_hash, internal_txs))
            z.append(appendAllTx(contract_hash, contract_txs))
        else:
            print("IDK")
        txs.append(z)

    # Try to interpret transactions

    for tx in txs:
        if not tx[0]:  # no normal tx associated, smart contract call only AFAIK
            if tx[1]:  # only seen these associated with eth transfer from contract address
                tx_type = tx[1]['type']
                contract_address = tx[1]['contract_address']
                if tx[1]['is_error']:
                    amount = 0
                else:
                    amount = Web3.fromWei(tx[1]['value'], 'ether').real
                txHash = tx[1]['hash']

                if tx[1]['to'].lower() == p.address.lower():
                    p.buy('ETH', amount, txHash)
                    print("\t received", str(amount), 'ETH', 'from', tx[1]['from'])
                elif tx[1]['from'].lower() == p.address.lower():
                    p.sell('ETH', amount, txHash)
                    print("\t sent", str(amount), 'ETH', 'to', tx[1]['to'])
                else:
                    print('\ttokens not sent to or from address being scanned')
                    print('\t', i)

        elif not tx[1] and not tx[2]:  # no internal smart contract txs, and not an erc20 tx, can also be an approve tx (how to handle??)
            if tx[0]['is_error']:
                amount = 0
            else:
                amount = Web3.fromWei(tx[0]['value'], 'ether').real
            txFee = Web3.fromWei(tx[0]['gas_price']*tx[0]['gas_used'], 'ether').real
            txHash = tx[0]['hash']

            if tx[0]['to'].lower() == p.address.lower():
                p.buy('ETH', amount, txHash)
                print('received ' + str(amount) + ' Eth')
            elif tx[0]['from'].lower() == p.address.lower():
                p.sell('ETH', amount, txHash, txFee=txFee)
                print('sent ' + str(amount) + ' Eth')

        elif not tx[1]:  # not an internal smart contract tx, so far i've only seen this happen for buying shitcoins or contract calls
            if isinstance(tx[2], list):  # if there are multiple erc20 txs, its likely not a shitcoin purchase
                print("some kind of smart contract call going on:")
                txFee = Web3.fromWei(tx[0]['gas_price'] * tx[0]['gas_used'], 'ether').real
                p.sell('ETH', 0, tx[0]['hash'], txFee=txFee)
                for i in tx[2]:
                    token_name = i['token_name']
                    token_symbol = i['token_symbol']
                    contract_address = i['contract_address']
                    if tx[0]['is_error']:
                        amount = 0
                    else:
                        amount = i['value'] / pow(10, i['token_decimal'])
                    p.addToken(token_name, contract_address, token_symbol, decimals=i['token_decimal'])
                    txHash = i['hash']

                    if i['to'].lower() == p.address.lower():
                        p.buy(contract_address, amount, txHash)
                        print("\t received", str(amount), token_symbol, 'from', i['from'])
                    elif i['from'].lower() == p.address.lower():
                        p.sell(contract_address, amount, txHash)
                        print("\t sent", str(amount), token_symbol, 'to', i['to'])
                    else:
                        print('\ttokens not sent to or from address being scanned')
                        print('\t', i)

            elif isinstance(tx[2], dict):
                eth_spent = Web3.fromWei(tx[0]['value'], 'ether').real
                txHash = tx[0]['hash']
                txFee = Web3.fromWei(tx[0]['gas_price'] * tx[0]['gas_used'], 'ether').real
                token_name = tx[2]['token_name']
                token_symbol = tx[2]['token_symbol']
                contract_address = tx[2]['contract_address']

                p.sell('ETH', eth_spent, txHash, txFee=txFee)

                if tx[2]['to'].lower() != p.address.lower():
                    token_sent = tx[2]['value'] / pow(10, tx[2]['token_decimal'])
                    p.sell(contract_address, token_sent, txHash)
                    print('spent ' + str(eth_spent) + ' Eth, also sent ' + str(token_sent), token_symbol)
                else:
                    token_received = tx[2]['value'] / pow(10, tx[2]['token_decimal'])
                    p.addToken(token_name, contract_address, token_symbol, decimals=tx[2]['token_decimal'])
                    p.buy(contract_address, token_received, txHash)
                    print('spent ' + str(eth_spent) + ' Eth for ' + str(token_received), token_symbol)
            else:
                raise Exception('erc20 tx list is some kinda fucked')


        elif not tx[2]:  # idk what this means
            print('internal transaction stuff')
            txHash = tx[0]['hash']
            txFee = Web3.fromWei(tx[0]['gas_price'] * tx[0]['gas_used'], 'ether').real

            if tx[0]['is_error']:
                eth_sent=0
            else:
                eth_sent = Web3.fromWei(tx[0]['value'], 'ether').real
            if tx[1]['is_error']:
                eth_received = 0
            else:
                eth_received = Web3.fromWei(tx[1]['value'], 'ether').real

            if eth_sent>=eth_received:
                p.sell('ETH',eth_sent-eth_received, txHash, txFee=txFee)
            else:
                p.buy('ETH', eth_received-eth_sent, txHash, txFee=txFee)

        else:  # internal tx, and erc20 tx.
            eth_sent = 0
            if tx[0]['to'].lower() != p.address.lower():  # if the tx sends eth to another wallet
                eth_sent += Web3.fromWei(tx[0]['value'], 'ether').real
            else:  # if the tx receives eth
                eth_sent -= Web3.fromWei(tx[0]['value'], 'ether').real
            if tx[1]['to'].lower() != p.address.lower():  # if the internal tx sends eth to another wallet
                eth_sent += Web3.fromWei(tx[1]['value'], 'ether').real
            else:  # if the internal tx receives eth
                eth_sent -= Web3.fromWei(tx[1]['value'], 'ether').real

            token_name = tx[2]['token_name']
            token_symbol = tx[2]['token_symbol']
            contract_address = tx[2]['contract_address']
            token_amount = tx[2]['value'] / pow(10, tx[2]['token_decimal'])
            txHash = tx[0]['hash']
            txFee = Web3.fromWei(tx[0]['gas_price'] * tx[0]['gas_used'], 'ether').real

            if eth_sent >= 0:
                p.sell('ETH', eth_sent, txHash, txFee=txFee)
            else:
                p.buy('ETH', eth_sent*-1, txHash, txFee=txFee)

            p.addToken(token_name, contract_address, token_symbol, decimals=tx[2]['token_decimal'])
            if tx[2]['to'].lower() != p.address.lower():
                p.sell(contract_address, token_amount, txHash)
                print('sold ' + str(token_amount), token_symbol + ' for ' + str(eth_sent) + ' Eth')
            else:
                p.buy(contract_address, token_amount, txHash)
                print('bought ' + str(token_amount), token_symbol + ' for ' + str(eth_sent*-1) + ' Eth')

    print("done")

def appendAllTx(transactionHash, txList):
    y = []
    i =0
    while (transactionHash == txList[0]['hash']):
        y.append(txList[0])
        txList.pop(0)
        i+=1
        if not txList:
            break
    if len(y) == 1:
        return y[0]
    else:
        return y


if __name__ == "__main__":
    main()


