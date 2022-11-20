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

def get_normal_transactions(p: Portfolio) -> list[objects.NormalTransaction]:
    normal_tx = client.get_transactions_by_address(p.address)
    transactions = []
    if len(normal_tx) == 0: return
    for tx in normal_tx:
        tmp = objects.NormalTransaction(tx)
        transactions.append(tmp)
    
    return transactions

def get_internal_transactions(p: Portfolio) -> list[objects.InternalTransaction]:
    internal_tx = client.get_transactions_by_address(p.address, tx_type='internal')
    transactions = []
    if len(internal_tx) == 0: return
    for tx in internal_tx:
        tmp = objects.InternalTransaction(tx)
        transactions.append(tmp)

    return transactions

def get_contract_transactions(p: Portfolio) -> list[objects.ContractTransaction]:
    contract_tx = client.get_token_transactions(address=p.address)
    transactions = []
    if len(contract_tx) == 0: return
    for tx in contract_tx:
        tmp = objects.ContractTransaction(tx)
        transactions.append(tmp)

    return transactions

def get_all_transactions(p: Portfolio) -> list[objects.Transaction]:
    normal_tx = get_normal_transactions(p)
    internal_tx = get_internal_transactions(p)
    contract_tx = get_contract_transactions(p)

    # Testing
    if internal_tx is not None: normal_tx.extend(internal_tx)
    if contract_tx is not None: normal_tx.extend(contract_tx)
        
    return normal_tx


# Testing
if __name__ == '__main__':
    address = '0xD29f9244beB3bfA4C4Ff354D913a481163E207a6'
    p = Portfolio(address)
    
    contract_tx = client.get_token_transactions(address=p.address)
    pp.pprint(contract_tx)


