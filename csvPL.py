import numpy as np
import pandas as pd
from dateutil.parser import parse
from datetime import datetime
import sys

class Token2:

    def __init__(self, symbol, pairCurrency):

        self.symbol = symbol
        self.pair = pairCurrency

        self.balanceHistory = []
        self.balance = 0
        self.p_l = 0  # buying is loss, selling is profit

    def buy(self, amount, value=0):
        self.balance += amount
        self.balanceHistory.append(self.balance)
        self.p_l -= value  # value of the tx in pair currency

    def sell(self, amount, value=0):
        self.balance -= amount
        self.balanceHistory.append(self.balance)
        self.p_l+= value


class Portfolio2:
    def __init__(self, address, tokens=[]):
        self.address = address
        self.tokens = tokens

        self.pairs = ['ETH', 'WETH', 'USDC']  # add these by default and dont track p/l
        for p in self.pairs:
            self.addToken(p)

    def isInstantiated(self, symbol):  # check to see if token has already been instantiated
        for i in self.tokens:
            if i.symbol == symbol:
                return True
        return False

    def addToken(self, symbol, pCurr=None):
        if not self.isInstantiated(symbol):
            t = Token2(symbol, pCurr)
            self.tokens.append(t)
            return t

    def findTokenBySymbol(self, symbol, pCurr):
        for i in self.tokens:
            if i.symbol.lower() == symbol.lower():
                return i
        return self.addToken(symbol, pCurr=pCurr)

    def buy(self, symbol, amount, value=0, pCurr='ETH', txFee=0, feeCurrency='ETH'):
        token = self.findTokenBySymbol(symbol, pCurr)
        token.buy(amount, value=0 if symbol in self.pairs else value) # dont track p_l on base currencies
        self.findTokenBySymbol(feeCurrency, pCurr).sell(txFee)
        # print("New", token.symbol, "balance: ", str(token.balance), token.symbol)

    def sell(self, symbol, amount, value=0, pCurr='ETH', txFee=0, feeCurrency='ETH'):
        token = self.findTokenBySymbol(symbol, pCurr)
        token.sell(amount, value=0 if symbol in self.pairs else value) # dont track p_l on base currencies
        self.findTokenBySymbol(feeCurrency, pCurr).sell(txFee)
        # print("New", token.symbol, "balance: ", str(token.balance), token.symbol)


# total arguments
n = len(sys.argv)
infile = sys.argv[1]
# infile = 'zerion_output2.csv'
outfile = 'output.xlsx'
try:
    outfile = sys.argv[2]
except:
    print('No output file specified, sending it to output.xlsx')

p = Portfolio2(None)

# Remove retarded bit at start of csv from zerion
with open(infile, 'r', encoding='utf8') as file:
    text = file.read()
with open(infile, 'w', encoding='utf8') as file:
    # Delete
    new_text = text.replace('data:text/csv;charset=utf-8,', '').replace('\r', '')
    # Write
    file.write(new_text)


df = pd.read_csv(infile, header=0, usecols=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,21], encoding_errors='replace')
parsed = df[['Timestamp', 'Transaction Type', 'Buy Amount', 'Buy Currency', 'Sell Amount', 'Sell Currency', 'Fee Amount', 'Fee Currency']]


for i, r in parsed.iterrows():
    # date = str(parse(r[0]))[:10]
    date = parse(r[0])
    txType = r[1]
    bAmount = r[2]
    bCurr = r[3]
    sAmount = r[4]
    sCurr = r[5]
    fAmount = r[6]
    fCurr = r[7]

    # process tx data
    if txType == 'trade':
        # some tx have multiple buy/sells split by \n
        bAmount = str(bAmount).split('\r\n')
        bCurr = bCurr.split('\r\n')
        sAmount = str(sAmount).split('\r\n')
        sCurr = sCurr.split('\r\n')

        for i in range(len(bCurr)):
            p.buy(bCurr[i], float(bAmount[i]), value=float(sAmount[i] if i < len(sAmount) else 0), pCurr=sCurr[0], txFee=float(fAmount) if i==0 else 0, feeCurrency=fCurr)
        for i in range(len(sCurr)):
            p.sell(sCurr[i], float(sAmount[i]), value=float(bAmount[i] if i < len(bAmount) else 0), pCurr=bCurr[0])

p_l = []
for t in p.tokens:
    p_l.append([t.symbol, t.balance, t.p_l, t.pair])


pl_percoin = pd.DataFrame(p_l, columns=['Symbol', 'Balance', 'P/L', 'Pair'])

pl_percoin.to_excel(outfile, encoding='utf-8')
print('done')




