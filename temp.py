"""
Refactored version of getAccountBalances.py

~Devon Gough
"""
import os
import pprint
import etherscan
from objects import Portfolio
from dotenv import load_dotenv

load_dotenv()

ES_API_KEY = os.getenv('ES_API_KEY')

client = etherscan.Client(api_key=ES_API_KEY, cache_expire_after=5)
pp = pprint.PrettyPrinter(indent=4)

def get_transactions(p: Portfolio):
    contract_tx = client.get_token_transactions(p.address)
    return contract_tx



# Testing
if __name__ == '__main__':
    address = '0xD29f9244beB3bfA4C4Ff354D913a481163E207a6'
    p = Portfolio(address)
    tx = get_transactions(p)
    pp.pprint(tx)
