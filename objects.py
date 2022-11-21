import pprint

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
        """
        Initializes a Transaction obj, expecting args to be the return
        from an etherscan api get_transactins_by_address() or
        get_token_transactions().
        """
        self.block_number          = args['block_number']
        self.from_                 = args['from']
        self.gas                   = args['gas']
        self.gas_used              = args['gas_used']
        self.hash                  = args['hash']
        self.input                 = args['input']
        self.timestamp             = args['timestamp']
        self.to                    = args['to']
        self.value                 = args['value']

    def __str__(self) -> str:
        return pprint.pformat(self.__dict__)

    def __repr__(self) -> str:
        return f"Transaction({self.block_number},{self.from_},{self.gas},{self.gas_used},{self.hash},{self.input},{self.timestamp},{self.to},{self.value}"
       
    def __lt__(self, other):
        return self.block_number < other.block_number
        
    def is_incoming(self, p:Portfolio) -> bool:
        """Returns true if the transaction is going into the portfolio address"""
        return self._to.lower() == p.address.lower() 

class NormalTransaction(Transaction):
    def __init__(self, args:dict) -> None:
        super().__init__(args)
        self.block_hash            = args['block_hash']
        self.confirmations         = args['confirmations']
        self.cumulative_gas_used   = args['cumulative_gas_used']
        self.gas_price             = args['gas_price']
        self.is_error              = args['is_error']

        self.nonce                 = args['nonce']
        self.transaction_index     = args['transaction_index']
        self.tx_receipt_status     = args['tx_receipt_status']

        self.tx_type               = 'normal'


class InternalTransaction(Transaction):
    def __init__(self, args:dict):
        super().__init__(args)
        self.contract_address  = args['contract_address']
        self.error_code        = args['error_code']
        self.is_error          = args['is_error']
        self.trace_id          = args['trace_id']
        self.type              = args['type']

        self.tx_type           = 'internal'
        
class ContractTransaction(Transaction):
    def __init__(self, args:dict) -> None:
        super().__init__(args)
        self.block_hash             = args['block_hash']
        self.confirmations          = args['confirmations']
        self.contract_address       = args['contract_address']
        self.cumulative_gas_used    = args['cumulative_gas_used']
        self.gas_price              = args['gas_price']
        self.nonce                  = args['nonce']
        self.token_decimal          = args['token_decimal']
        self.token_name             = args['token_name']
        self.token_symbol           = args['token_symbol']
        self.transaction_index      = args['transaction_index']

        self.tx_type                = 'contract'

class MultiTransaction(Transaction):
    def __init__(self, args:dict, tx:list[Transaction]=[]) -> None:
        super().__init__(args)

        self.tx_type = 'multi'

        self._set_sub_tx(tx)

    def _set_sub_tx(self, tx:list[Transaction]=[]) -> None:
        pass
