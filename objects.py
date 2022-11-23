import pprint

# TODO: Solve the circular references
class Token:
    """
    TODO
    """

    def __init__(self, args:dict) -> None:
        self.contract_address = args['contract_address']
        self.decimals = args['decimals']
        self.name = args['name']
        self.symbol = args['symbol']

        # portfolio stuff
        self.token_amount = 0
        self.portfolio = args['portfolio']
        self.token_transaction_history = []
        

class Portfolio:
    """A tracker for token holdings and prices

    Parameters:
        address (str): The hexadecimal address of the wallet.
    """

    def __init__(self, address: str) -> None:
        self.address = address
        self.tokens = []

        self._all_transactions = self._pull_transactions()

        # add eth
        self.add_token({"portfolio":self,"name": "Ether","pair": None,"contract_address": None, "decimals": 18, "symbol": "ETH"})

    def _pull_transactions(self):
        """This will call temp.py or whatever its called
        in the future when its done"""
        pass

    def add_token(self, token_args:dict) -> None:
        """Create and add a token object"""
        
        """
        Args needed for Token:
        ca
        
        name
        symbol
        decimals
        uni_v2_pair
        """
        temp = Token(token_args)
        self.tokens.append(temp)

    def increment_balance(self, token, amt, increase:bool=True):
        """For when tokens get sent into an address"""

        # find the token in the list within the portfolio

        # should be a one element list, 
        singular_token = [x for x in self.tokens if x.name.lower() == token.lower()]
        
        # TODO test this in a testing class eventually
        if singular_token:
            if len(singular_token) > 1:
                print('bad')

            t = singular_token[0]
            
            if increase:
                t.token_amount += amt
            else:
                t.token_amount -= amt
        else:
            print(f'token: {token} is not recognized')
    

class PaperPortfolio(Portfolio):

    def __init__(self, balance: int = 1000) -> None:
        super().__init__()
        self.fake_balance = balance

    def paper_buy():
        pass

    def paper_sell():
        pass


class Transaction:
    """The parent class to all types of Transactions

    Args should be provided in a single dictionary.  Ideally args should be returned from
    the etherscan client api request.

    Attributes:
        block_number (int)
        from (str)
        gas (int)
        gas_used (int)
        hash (str)
        input (str)
        timestamp (int)
        to (str)
        value (int)

    Args:
        args (dict): A dictionary of the structure -
        args{
            block_number: 0,
            from: "",
            gas: 0,
            gas_used: 0,
            hash: "",
            input: "",
            timestamp: 0,
            to: "",
            value: 0
        }
    """

    def __init__(self, args: dict, c: bool = False) -> None:
        self.block_number = args["block_number"]
        self.gas = args["gas"]
        self.gas_used = args["gas_used"]
        self.hash = args["hash"]
        self.input = args["input"]
        self.timestamp = args["timestamp"]
        self.to = args["to"]
        self.value = args["value"]

        # c flag is to copy from an existing Transaction object, where 'from' is not an attribute (its 'from_')
        if c:
            self.from_ = args["from_"]
        else:
            self.from_ = args["from"]

    def __str__(self) -> str:
        return pprint.pformat(self.__dict__)

    def __repr__(self) -> str:
        return f"Transaction({self.block_number},{self.from_},{self.gas},{self.gas_used},{self.hash},{self.input},{self.timestamp},{self.to},{self.value}"

    def __lt__(self, other):
        return self.block_number < other.block_number

    def __eq__(self, other):
        return self.hash == other.hash

    def is_incoming(self, p: Portfolio) -> bool:
        """Returns true if the transaction is going into the portfolio address"""
        return self.to.lower() == p.address.lower()


class NormalTransaction(Transaction):
    """Contains information on a normal transaction

    Contains a transaction returned from client.get_transactions_by_address(p.address)

    Attributes:
        block_hash (str)
        block_number (int)
        confirmations (int)
        cumulative_gas_used (int)
        gas (int)
        gas_price (int)
        gas_used (int)
        hash (str)
        input (str)
        is_error (bool)
        nonce (int)
        timestamp (int)
        to (str)
        transaction_index (int)
        tx_type (str)
        value (int)

    Args:
        args (dict): A dictionary of the structure -
        args{
            block_hash: "",
            block_number: 0,
            confirmations: 0,
            cumulative_gas_used: 0,
            gas: 0,
            gas_price: 0,
            gas_used: 0,
            hash: "",
            input: "",
            is_error: False,
            nonce: 0,
            timestamp: 0,
            to: "",
            transaction_index: 0,
            tx_type: "",
            value: 0,
        }
    """

    def __init__(self, args: dict, c: bool = False) -> None:
        super().__init__(args)
        self.block_hash = args["block_hash"]
        self.confirmations = args["confirmations"]
        self.cumulative_gas_used = args["cumulative_gas_used"]
        self.gas_price = args["gas_price"]
        self.is_error = args["is_error"]

        self.nonce = args["nonce"]
        self.transaction_index = args["transaction_index"]
        self.tx_receipt_status = args["tx_receipt_status"]

        self.tx_type = "normal"


class InternalTransaction(Transaction):
    """Contains information on an internal transaction
    
    Contains a transaction returned from client.get_transactions_by_address(p.address,tx='internal').

    Attributes:
        block_number (int)
        contract_address (str)
        error_code (str)
        from (str)
        gas (int)
        gas_used (int)
        hash (str)
        input (str)
        is_error (bool)
        timestamp (int)
        to (str)
        trace_id (str)
        tx_type (str)
        type (str)
        value (int)

    Args:
        args (dict): A dictionary of the structure -
        args{
        block_number: 0,
        contract_address: "",
        error_code: "",
        from: "",
        gas: 0,
        gas_used: 0,
        hash: "",
        input: "",
        is_error: False,
        timestamp: 0,
        to: "",
        trace_id: "",
        tx_type: "",
        type: "",
        value: 0,
        }
    """

    def __init__(self, args: dict, c: bool = False):
        """TODO"""
        super().__init__(args)
        self.contract_address = args["contract_address"]
        self.error_code = args["error_code"]
        self.is_error = args["is_error"]
        self.trace_id = args["trace_id"]
        self.type = args["type"]

        self.tx_type = "internal"


class ContractTransaction(Transaction):
    """Contains information on an contract transaction
    
    Contains a transaction returned from client.get_token_transactions(address=p.address)

    Attributes:
        block_hash (str)
        block_number (int)
        confirmations (int)
        contract_address (str)
        cumulative_gas_used (int)
        from (str)
        gas (int)
        gas_price (int)
        gas_used (int)
        hash (str)
        input (str)
        nonce (int)
        timestamp (int)
        to (str)
        token_decimal (int)
        token_name (str)
        token_symbol (str)
        transaction_index (int)
        tx_type (str)
        value (int)

    Args:
        args (dict): A dictionary of the structure -
        args{
            block_hash: "",
            block_number: 0,
            confirmations: 0,
            contract_address: "",
            cumulative_gas_used: 0,
            from: "",
            gas: 0,
            gas_price: 0,
            gas_used: 0,
            hash: "",
            input: "",
            nonce: 0,
            timestamp: 0,
            to: "",
            token_decimal: 0,
            token_name: "",
            token_symbol: "",
            transaction_index: 0,
            tx_type: "",
            value: 0,
        }
    """

    def __init__(self, args: dict, c: bool = False) -> None:
        super().__init__(args)
        self.block_hash = args["block_hash"]
        self.confirmations = args["confirmations"]
        self.contract_address = args["contract_address"]
        self.cumulative_gas_used = args["cumulative_gas_used"]
        self.gas_price = args["gas_price"]
        self.nonce = args["nonce"]
        self.token_decimal = args["token_decimal"]
        self.token_name = args["token_name"]
        self.token_symbol = args["token_symbol"]
        self.transaction_index = args["transaction_index"]

        self.tx_type = "contract"


class MultiTransaction(Transaction):
    """Contains information on an contract transaction
    
    Contains a transaction returned from client.get_token_transactions(address=p.address)

    Attributes:
        block_number (int)
        contract_transaction (ContractTransaction)
        from (str)
        gas (int)
        gas_used (int)
        hash (str)
        input (str)
        internal_transaction (InternalTransaction)
        normal_transaction (NormalTransaction)
        timestamp (int)
        to (str)
        value (int)
        
    Args:
        args (dict): A dictionary of the structure -
        args{
            block_number: 0,
            from: "",
            gas: 0,
            gas_used: 0,
            hash: "",
            input: "",
            timestamp: 0,
            to: "",
            value: 0
        }
    """

    def __init__(self, args: dict, c: bool = False) -> None:
        super().__init__(args, c)

        self.normal_transaction = None
        self.internal_transaction = None
        self.contract_transaction = None

        self.tx_type = "multi"

    def set_normal_transaction(self, n: NormalTransaction) -> None:
        """Sets the normal_transaction pointer to the supplied NormalTransaction object"""
        self.normal_transaction = n

    def set_internal_transaction(self, i: InternalTransaction) -> None:
        """Sets the internal_transaction pointer to the supplied InternalTransaction object"""
        self.internal_transaction = i

    def set_contract_transaction(self, c: ContractTransaction) -> None:
        """Sets the contract_transaction pointer to the supplied ContractTransaction object"""
        self.contract_transaction = c
