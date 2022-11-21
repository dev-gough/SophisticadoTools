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
from itertools import zip_longest

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

def handle_multi_tx(transactions:list[objects.Transaction]) -> list[objects.Transaction]:
    """
    Checks for multiple transaction types with the same hash, molds them together
    into one object (with pointers to the other Transaction objects), removes the
    Transaction objects that share the same hash from transactions, then add the
    one MultiTransaction in its place according to block_number.
    """
    cache = []
    output_transactions = []
    zipper = transactions[1:]
    # Needs one pass through the list
    for tx ,lookahead in zip_longest(transactions,zipper):
        if cache and cache == tx:
            # Create the temp MultiTransaction obj so we can point the right tx to it later.
            tmp = objects.MultiTransaction(tx.__dict__,True)
            # check ahead one element
            try:
                if lookahead is not None and lookahead == cache:
                    # all 3 types are present.
                    txs = [tx,cache,lookahead]
                else:
                    txs = [tx,cache]
            except Exception as err:
                print(err)
            
            for t in txs:
                if t.tx_type    == 'normal': tmp.set_normal_transaction(t)
                elif t.tx_type  == 'internal': tmp.set_internal_transaction(t)
                elif t.tx_type  == 'contract': tmp.set_contract_transaction(t)

            output_transactions.append(tmp)
        if lookahead is not None and lookahead != tx:
            output_transactions.append(tx)
        cache = tx
    output_transactions.sort()
    return output_transactions

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
        normal_tx = handle_multi_tx(normal_tx)
        
    return normal_tx


# Testing
if __name__ == '__main__':
    address = '0xD29f9244beB3bfA4C4Ff354D913a481163E207a6'
    p = Portfolio(address)
    
    tx = get_all_transactions(p)

    for t in tx:
        print(t)