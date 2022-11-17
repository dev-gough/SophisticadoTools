import requests

from datetime import datetime
from pprint import pprint

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
	# TheGraphQL requires lowercase addresses
	pair_address = pair_address.lower()
	
	# Converts a datetime instance to a unix timestamp
	if isinstance(date_gt, datetime):
		date_gt = int(date_gt.timestamp())

	query = f"""{{pairDayDatas(where:{{date_gt: {date_gt} pairAddress: "{pair_address}"}})
		{{date token0 {{name symbol decimals}} reserve0 token1 {{name symbol decimals}} reserve1}}}}"""

	response = requests.post('https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2','',json={'query' : query})

	if response.status_code == 200:
		return response.json()['data']['pairDayDatas']
	else:
		raise Exception('Query failed.  Return code is {}.		{}'.format(response.status_code, query))

def get_prices(daily_data:list, time) -> dict:
	"""
	Returns the daily USD prices of the token from the provided token pairing.

	Parameters:
		time (int/datetime): Unix timestamp/datetime object passed through from main method.
		daily_data (list): The list of daily token pairings returned from run_query() 
	
	Returns:
		daily_price_data (dict): A dictionary of structure {timestamp: $USD price}
	"""

	# Converts a datetime instance to a unix timestamp
	if isinstance(time, datetime):
		time = int(time.timestamp())

	daily_price_data = {}
	use_eth = False

	"""
	TODO describe this better

	daily_data is a list of nested dictionaries, so here we are checking the first day's data, sub-dictionary token0,
	for attribute symbol, and seeing if it is eth or wrapped eth for either of the two tokens in the pair.

	token0_reserve is a boolean indicating whether token0 is the reserve or token1.
	"""
	if (daily_data[0]['token0']['symbol'].lower() in ('weth', 'eth')) :
		use_eth = True
		token0_reserve = True
	elif (daily_data[0]['token1']['symbol'].lower() in ('weth', 'eth')):
		use_eth = True
		token0_reserve = False
	elif (daily_data[0]['token0']['symbol'].lower() in ('usdc')):
		use_eth = False
		token0_reserve = True
	elif (daily_data[0]['token1']['symbol'].lower() in ('usdc')):
		use_eth = False
		token0_reserve = False

	if use_eth:
		# Get eth daily price
		daily_eth_prices = get_eth_usd(time)

		# Loop through each day, calculating price
		for day in daily_data:
			eth_price = daily_eth_prices[day['date']]
			
			if token0_reserve:
				reserve = eth_price * float(day['reserve0'])
				asset = float(day['reserve1'])
			elif not token0_reserve:
				reserve = eth_price * float(day['reserve1'])
				asset = float(day['reserve0'])
			
			price = reserve/asset

			daily_price_data.update({day['date']:price})
	else:
		# using usdc
		print('here o7')
		for day in daily_data:
			if token0_reserve:
				price = float(day['reserve0']) / float(day['reserve1'])
			else: 
				price = float(day['reserve1']) / float(day['reserve0'])
			
			daily_price_data.update({day['date']:price})

	return daily_price_data

def get_eth_usd(time) -> dict:
	"""
	Get daily eth prices in $USD from time until now.

	Parameters:
		time (int/datetime): Unix timestamp or datetime object, date you want to start the prices from.

	Returns:
		daily_eth_prices (dict): A dictionary of structure {timestamp: $USD price}
	"""
	
	# Converts from datetime to unix timestamp
	if isinstance(time, datetime):
		time = int(time.timestamp())
	
	daily_eth_prices = {}
	eth_pair = '0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc'
	daily_eth_data = run_query(eth_pair,time)

	# Loop through each day
	for day in daily_eth_data:
		timestamp = day['date']
		usdc = int(float(day['reserve0']))
		weth = int(float(day['reserve1']))

		price = usdc/weth

		daily_eth_prices.update({timestamp:price})

	return daily_eth_prices

def print_prices(prices:dict, precision:int = 2) -> None:
	"""
	Prints price data returned from get_prices() into a more human readable format

	Parameters:
		prices (dict): Returned from get_prices()
		precision (int): How many decimals for displaying $USD price.

	Returns:
		None

	Expecting prices to have structure {timestamp: $USD price}
	"""
	for timestamp, eth_price in prices.items():
		date = datetime.fromtimestamp(timestamp)
		print(f'{date}: ${eth_price:.{precision}f}')

# Testing Code
if __name__ == '__main__':
	# Returns list of day token data.
	dt = datetime.fromisoformat("2022-11-01")
	spiral_pair = '0x81AE721d8B600a59A8a7196b1264FB976DB2cc50'
	harmony_pair = '0x1437eABf0c60DA8478A9E2Bf1569AE432e72C465'

	prices = get_prices(run_query(spiral_pair,dt),dt)
	print_prices(prices,2)

	prices2 = get_prices(run_query(harmony_pair,dt),dt)
	print_prices(prices2,20)
