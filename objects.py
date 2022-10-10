class Token:

    def __init__(self, name, contract_address, symbol, decimals=9, total_supply=None, token_pair='ETH'):

        self.name = name
        self.contract_address = contract_address
        self.symbol = symbol
        self.decimals = decimals
        self.total_supply = total_supply
        self.token_pair = token_pair

        self.balance = 0
        self.token_price = None

    def getContractAddress(self):
        return self.contract_address

    def getSymbol(self):
        return self.symbol

    def getDecimals(self):
        return self.decimals

    def getTotalSupply(self):
        return self.total_supply

    def getBalance(self):
        return self.balance

    def setContractAddress(self, contract_address):
        self.contract_address = contract_address

    def setSymbol(self, symbol):
        self.symbol = symbol

    def setDecimals(self, decimals):
        self.decimals = decimals

    def setTotalSupply(self, total_supply):
        self.total_supply = total_supply

    def buy(self, amount):
        self.balance += amount
        print("New", self.symbol, "balance: ", str(self.balance), self.symbol)

    def sell(self, amount):
        self.balance -= amount
        print("New", self.symbol, "balance: ", str(self.balance), self.symbol)


class Portfolio:
    def __init__(self, address, tokens=[]):
        self.address = address
        self.tokens = tokens

        self.addToken('Ethereum', 'ETH', 'ETH', decimals=None, total_supply=None, token_pair=None)  # eth is automatically added

    def isInstantiated(self, contract_address):  # check to see if token has already been instantiated
        for i in self.tokens:
            if i.getContractAddress().lower() == contract_address.lower():
                return True
        return False

    def addToken(self, name, contract_address, symbol, decimals=9, total_supply=None, token_pair='ETH'):
        if not self.isInstantiated(contract_address):
            t = Token(name, contract_address, symbol, decimals=decimals, total_supply=total_supply, token_pair=token_pair)
            self.tokens.append(t)

    def findTokenByCA(self, contract_address):
        for i in self.tokens:
            if i.getContractAddress().lower() == contract_address.lower():
                return i

    def buy(self, contract_address, amount):
        self.findTokenByCA(contract_address).buy(amount)

    def sell(self, contract_address, amount):
        self.findTokenByCA(contract_address).sell(amount)
