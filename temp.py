"""
Refactored version of getAccountBalances.py

~Devon Gough
"""

import os
import pprint
import etherscan
import objects
from objects import Portfolio
from dotenv import load_dotenv

load_dotenv()

ES_API_KEY = os.getenv('ES_API_KEY')

client = etherscan.Client(api_key=ES_API_KEY, cache_expire_after=5)
pp = pprint.PrettyPrinter(indent=4)

# TODO: once done this file implement multi_tx checking
def objectify(transactions:dict, tx_type:objects.Transaction, multi_tx: list[objects.Transaction]=[]) -> list[objects.Transaction]:
    tx_objs = []
    for tx in transactions:
        t = tx_type(tx)
        tx_objs.append(t)
    
    return tx_objs
    
def get_normal_transactions(p: Portfolio) -> list[objects.NormalTransaction]:
    normal_tx = client.get_transactions_by_address(p.address)
    return objectify(normal_tx,objects.NormalTransaction) if len(normal_tx) != 0 else None

def get_internal_transactions(p: Portfolio) -> list[objects.InternalTransaction]:
    internal_tx = client.get_transactions_by_address(p.address, tx_type='internal')
    return objectify(internal_tx,objects.InternalTransaction) if len(internal_tx) != 0 else None


def get_contract_transactions(p: Portfolio) -> list[objects.ContractTransaction]:
    contract_tx = client.get_token_transactions(address=p.address)
    return objectify(contract_tx,objects.ContractTransaction) if len(contract_tx) != 0 else None


# TODO: Add logic for finding MultiTransactions
def get_all_transactions(p: Portfolio, sorted:bool = True) -> list[objects.Transaction]:
    normal_tx = get_normal_transactions(p)
    internal_tx = get_internal_transactions(p)
    contract_tx = get_contract_transactions(p)

    if internal_tx is not None: normal_tx.extend(internal_tx)
    if contract_tx is not None: normal_tx.extend(contract_tx)

    if sorted:
        normal_tx.sort()
        
    return normal_tx


# Testing
if __name__ == '__main__':
    address = '0xD29f9244beB3bfA4C4Ff354D913a481163E207a6'
    p = Portfolio(address)
    
    tx = get_all_transactions(p)

    for t in tx:
        print(t)

