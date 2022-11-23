"""
Refactored version of getAccountBalances.py.

~Devon Gough
"""

import os
import pprint
import etherscan
import objects
from objects import Portfolio
from dotenv import load_dotenv
from itertools import zip_longest
from web3 import Web3

load_dotenv()

ES_API_KEY = os.getenv('ES_API_KEY')

client = etherscan.Client(api_key=ES_API_KEY, cache_expire_after=5)
pp = pprint.PrettyPrinter(indent=4)


def objectify(transactions: list,
              tx_type: objects.Transaction) -> list[objects.Transaction]:
    """Turns a transaction list into a list of Transaction objects

    Args:
        transactions (list): A list of dictionaries of attributes and values.
        tx_type (objects.Transaction): Which type the Transaction object should be.

    Returns:
        tx_objs (list[objects.Transaction]): The list of Transaction objects.
    """
    tx_objs = []
    for tx in transactions:
        t = tx_type(tx)
        tx_objs.append(t)

    return tx_objs


def handle_multi_tx(
        transactions: list[objects.Transaction]) -> list[objects.Transaction]:
    """Replaces (hashes with multiple transactions) with one MultiTransaction object.

    Some transactions will have the same hash, but be different types, and thus have different data.
    I want the Portfolio object to have one list of Transaction objects with non-repeating hashes,
    which is the motivation behind this.

    Scans the list of transactions, and if 2 or 3 are spotted with the same hash they are all added to the same
    MultiTransaction object, which is placed in the output list.  If the transaction hash is unique nothing happens
    and it is appended to the output list.  The list is finally sorted by block_number before being returned.

    Args:
        transactions (list[objects.Transaction]): A list of Transaction objects to check through.  Likely from get_all_transactions.
    
    Returns:
        output_transactions (list[objects.Transaction]): The modified list of transactions.
    """
    cache = []
    output_transactions = []

    # zipper is the same list as transactions, just offset by one and None tacked onto the end.
    zipper = transactions[1:]

    # needs one pass through the list, zip_longest is to have lookahead as well to try to find a third transaction.
    for tx, lookahead in zip_longest(transactions, zipper):
        if cache and cache == tx:  # == implemented by hash

            # create the temp MultiTransaction obj so we can point the right tx to it later.
            tmp = objects.MultiTransaction(tx.__dict__, True)

            # check ahead one element
            try:
                if lookahead is not None and lookahead == cache:
                    # all 3 types are present.
                    txs = [tx, cache, lookahead]
                else:
                    txs = [tx, cache]
            except Exception as err:
                print(err)

            # iterate through all transactions found with the same hash, then set the pointers.
            for t in txs:
                if t.tx_type == 'normal':
                    tmp.set_normal_transaction(t)
                elif t.tx_type == 'internal':
                    tmp.set_internal_transaction(t)
                elif t.tx_type == 'contract':
                    tmp.set_contract_transaction(t)

            output_transactions.append(tmp)

        # ensure we aren't adding a transaction back mistakenly
        if lookahead is not None and lookahead != tx:
            output_transactions.append(tx)

        # set the cache
        cache = tx

    output_transactions.sort()
    return output_transactions


def get_normal_transactions(p: Portfolio) -> list[objects.NormalTransaction]:
    """Returns a list of NormalTransaction objects given a Portfolio"""
    normal_tx = client.get_transactions_by_address(p.address)
    return objectify(normal_tx,
                     objects.NormalTransaction) if len(normal_tx) != 0 else None


def get_internal_transactions(
        p: Portfolio) -> list[objects.InternalTransaction]:
    """Returns a list of InternalTransaction objects given a Portfolio"""
    internal_tx = client.get_transactions_by_address(p.address,
                                                     tx_type='internal')
    return objectify(
        internal_tx,
        objects.InternalTransaction) if len(internal_tx) != 0 else None


def get_contract_transactions(
        p: Portfolio) -> list[objects.ContractTransaction]:
    """Returns a list of ContractTransaction objects given a Portfolio"""
    contract_tx = client.get_token_transactions(address=p.address)
    return objectify(
        contract_tx,
        objects.ContractTransaction) if len(contract_tx) != 0 else None


def get_all_transactions(p: Portfolio,
                         sorted: bool = True) -> list[objects.Transaction]:
    """Returns all types of transactions from a portfolio in a single list

    Args:
        p (Portfolio): The Porfolio object we want to scrape the transactions from.
        sorted (bool): True if you want the list sorted by block_number.

    Returns:
        normal_tx (list[objects.Transaction]): A (possibly sorted) list of Transaction objects.
    """

    # gather all 3 types of transactions
    normal_tx = get_normal_transactions(p)
    internal_tx = get_internal_transactions(p)
    contract_tx = get_contract_transactions(p)

    # append into 1 list
    if internal_tx is not None:
        normal_tx.extend(internal_tx)
    if contract_tx is not None:
        normal_tx.extend(contract_tx)

    if sorted:
        normal_tx.sort()
        normal_tx = handle_multi_tx(
            normal_tx)  # handling multiple transactions requires a sorted list

    return normal_tx

def process_transaction(p: Portfolio, t: objects.Transaction) -> None:
    """Process a single transaction and execute it's state change for the Portfolio
    TODO
    """
    # there are 6 different combinations of tx in a single tx object.

    if t.tx_type == "multi":
        # handle the 3 cases here
        pass
    else:
        # handle the other 3 cases here
        if t.tx_type == 'normal':
            # sending eth from 1 addr to another
            if t.is_error:
                amt = 0
                tx_fee = 0
            else:
                amt = Web3.fromWei(t.value, 'ether')
                tx_fee = Web3.fromWei((t.gas_price * t.gas_used), 'ether')
            
            if t.is_incoming(p):
                p.increment_balance('ether', amt)
            else:
                p.increment_balance('ether', amt+tx_fee, increase=False)

        elif t.tx_type == 'internal':
            """Seems to be transferring eth via a contract"""
            if t.is_error:
                amt = 0
            else:
                amt = Web3.fromWei(t.value, 'ether')
            
            if t.is_incoming(p):
                p.increment_balance('ether',amt)
            else:
                p.increment_balance('ether', amt+tx_fee, increase=False)

        elif t.tx_type == 'contract':
            print('check this out.')

# Testing
if __name__ == '__main__':
    address = '0xD29f9244beB3bfA4C4Ff354D913a481163E207a6'
    p = Portfolio(address)

    tx = get_all_transactions(p)
    
    for t in tx:
        process_transaction(p,t)
