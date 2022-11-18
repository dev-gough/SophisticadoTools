class Token:
    def __init__(self, token_addr: str) -> None:
        self.address = token_addr
        self.daily_price = {}
        
        self._setup()

        """
        
        want to automatically get and make attributes:
        
        self.name = name
        self.contract_address = contract_address
        self.symbol = symbol
        self.decimals = decimals
        self.total_supply = total_supply
        self.token_pairs = {}
        
        """
    
    def _setup(self):
        # Get the name of the token.
        pass

class Portfolio:
    """
    A tracker for token holdings and prices.

    Parameters:
        address (str): The hexadecimal address of the wallet.
        tokens (list): The list of tokens held in the wallet.
    """
    def __init__(self, address:str, tokens:list[Token] = []) -> None:
        self.address = address
        self.tokens = tokens

        # Will be used eventually for caching token prices.
        self.cache = {}

        # Will be list of all tx hashes
        self.transactions = {}
        self._pull_transactions()

        # TODO: Add usdc & eth as default.
        usdc = Token('usdc-addr')
        self.add_token(usdc)
   
    def add_token(self, token):
        self.tokens.append(token)

    def remove_dust(self):
        pass

    def buy():
        pass

    def sell():
        pass

    def daily_pl():
        pass

    def _pull_transactions(self):
        pass

class PaperPortfolio(Portfolio):
    def __init__(self, balance: int = 1000) -> None:
        super().__init__()
        self.fake_balance = balance

    def paper_buy():
        pass

    def paper_sell():
        pass

class Transaction():
    def __init__(self, args:dict) -> None:
        self._block_number          = args['block_number']
        self._from                  = args['from']
        self._gas                   = args['gas']
        self._gas_used              = args['gas_used']
        self._hash                  = args['hash']
        self._input                 = args['input']
        self._is_error              = args['is_error']
        self._timestamp             = args['timestamp']
        self._to                    = args['to']
        self._value                 = args['value']

class NormalTransaction(Transaction):
    def __init__(self, args:dict) -> None:
        super().__init__(args)
        self.tx_type                = 'normal'
        self._block_hash            = args['block_hash']
        self._confirmations         = args['confirmations']
        self._cumulative_gas_used   = args['cumulative_gas_used']
        self._gas_price             = args['gas_price']
        self._nonce                 = args['nonce']
        self._transaction_index     = args['transaction_index']
        self._tx_receipt_status     = args['tx_receipt_status']

class InternalTransaction(Transaction):
    def __init__(self, args:dict):
        super().__init__(args)
        self._contract_address  = args['contract_address']
        self._error_code        = args['error_code']
        self._trace_id          = args['trace_id']
        self._type              = args['type']
        
# TODO find example of these transactions, and alter top level Transaction class accordingly
class ContractTransaction():
    def __init__(self, args:dict) -> None:
        pass
