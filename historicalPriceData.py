import requests
import time

from datetime import datetime
from pprint import pprint

just_in_case = """{pairDayDatas(where:{date_gt: 1664668800 pairAddress: "0x81AE721d8B600a59A8a7196b1264FB976DB2cc50"})
		{date token0 {name symbol decimals} reserve0 token1 {name symbol decimals} reserve1}}"""

#TODO: Figure out variables in the json to query any pairAddress and date_gt.
#TODO: Get hourly data
def run_query(pair_address:(str), date_gt) -> dict:
	"""
	Returns the response from the Uniswap V2 Subgraph.

	Parameters:
		pair_address (str) : A hex string of the contract address for the Uniswap Pair.
		date_gt (int/datetime): Either unix timestamp or a datetime object.

	Returns:
		request.json() (dict): The JSON repsonse to the query.
	"""
	
	if isinstance(date_gt, datetime):
		date_gt = date_gt.timestamp()

	query = f"""{{pairDayDatas(where:{{date_gt: {date_gt} pairAddress: "{pair_address}"}})
		{{date token0 {{name symbol decimals}} reserve0 token1 {{name symbol decimals}} reserve1}}}}"""

	response = requests.post('https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2','',json={'query' : query})

	if response.status_code == 200:
		return response.json()
	else:
		raise Exception('Query failed.  Return code is {}.		{}'.format(response.status_code, query))

#TODO Get eth pools working.
def get_prices(unix_timestamp:int, tx:list, use_eth:bool = False, swap_reserves=False) -> dict:
	"""
	Takes in the list of pairDayDatas and spits out a 
	dictionary with the price in USDC or ETH

	Parameters:
		tx (list): A list of dictionaries returned from run_query()['data']['pairDayDatas']
		use_eth (bool): Set true if the Uniswap pair is using ETH instead of USDC.

	Returns:
		daily_price_data (dict): Simple dict of structure {date: int: price: float}
	"""
	daily_price_data = {}

	if use_eth:
		# Get the price data for eth.
		daily_eth_prices = run_query('0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc'.lower(),unix_timestamp)['data']['pairDayDatas']

		if len(tx) != len(daily_eth_prices):
			raise Exception("Something fucky wucky happened.")

		# Recursive call to get ETH/USDC per timestamp
		daily_eth_price_data = get_prices(unix_timestamp,daily_eth_prices,swap_reserves=True)

	for day in tx:
		reserve1 = float(day['reserve1'])
		reserve0 = float(day['reserve0']) if not use_eth else float(daily_eth_price_data[unix_timestamp])

		# TODO: Get this working automatically
		price = reserve1/reserve0 if swap_reserves else reserve0/reserve1
		
		
		daily_price_data.update({day['date']: price})

	return daily_price_data

def print_prices(prices:dict) -> None:
	"""
	Prints price data returned from get_prices() into a more human readable format

	Parameters:
		prices (dict): Returned from get_prices()

	Returns:
		None
	"""
	for k in prices:
		#Get the date from the Unix Time Stamp
		print(datetime.fromtimestamp(k).ctime())
		print('$'+ '{:.20f}'.format(prices[k]),'\n')



# Testing Code
if __name__ == '__main__':
	# Returns list of day token data.
	unix_timestamp = 1664668800
	spiral_pair = '0x81AE721d8B600a59A8a7196b1264FB976DB2cc50'
	harmony_pair = '0x1437eABf0c60DA8478A9E2Bf1569AE432e72C465'


	result = run_query(harmony_pair.lower(),unix_timestamp)['data']['pairDayDatas']
	prices = get_prices(unix_timestamp,result,use_eth=True)
	print_prices(prices)


0.000000008068615369240518
0.00000000000627682243
0.00000000000627682243  
