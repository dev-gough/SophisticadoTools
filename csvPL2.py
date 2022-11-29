import numpy as np
import pandas as pd
from dateutil.parser import parse
from datetime import datetime
import sys, getopt
import os
from dotenv import load_dotenv
from web3 import Web3
import etherscan

load_dotenv()

ES_ENDPOINT = os.getenv('ES_ENDPOINT')
ES_API_KEY = os.getenv('ES_API_KEY')
MAINNET_ENDPOINT = os.getenv('MAINNET_ENDPOINT')
w3 = Web3(Web3.HTTPProvider(MAINNET_ENDPOINT))
es = etherscan.Client(api_key=ES_API_KEY, cache_expire_after=5)


class Token2:

    def __init__(self, symbol, pairCurrency, dateSold):

        self.symbol = symbol
        self.pair = pairCurrency
        self.dateSold = dateSold

        self.balanceHistory = []
        self.balance = 0
        self.p_l = 0  # buying is loss, selling is profit
        self.fees = 0  # track tx fees separately from p/l because there is no guarantee that p/l pair is fee currency

    def buy(self, amount, value=[0, 0]):
        self.balance += amount
        self.balanceHistory.append(self.balance)
        self.p_l -= value[0]  # value of the tx in pair currency
        self.fees += value[1]

    def sell(self, amount, value=[0, 0]):
        self.balance -= amount
        self.balanceHistory.append(self.balance)
        self.p_l+= value[0]
        self.fees += value[1]


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

    def addToken(self, symbol, pCurr=None, date=None):
        if not self.isInstantiated(symbol):
            t = Token2(symbol, pCurr, date)
            self.tokens.append(t)
            return t

    def findTokenBySymbol(self, symbol, pCurr, date):
        for i in self.tokens:
            if i.symbol.lower() == symbol.lower():
                return i
        return self.addToken(symbol, pCurr=pCurr, date=date)

    def buy(self, symbol, amount, value, pCurr='ETH', txFee=0, feeCurrency='ETH', date=None):
        token = self.findTokenBySymbol(str(symbol), pCurr, date)
        # if token.symbol == 'PSYOP':
        #     print('breakpoint')
        # I should subtract TX fees from value for inclusion in P/L calculation but there is no way to reconcile different pairs. TOKEN could be paired with USDC and tx fee is in eth :////
        token.buy(amount, value=[0, 0] if symbol in self.pairs else [value, txFee])  # dont track p_l on base currencies
        self.findTokenBySymbol(str(feeCurrency), pCurr, date).sell(txFee)
        # print("New", token.symbol, "balance: ", str(token.balance), token.symbol)

    def sell(self, symbol, amount, value, pCurr='ETH', txFee=0, feeCurrency='ETH', date=None):
        token = self.findTokenBySymbol(str(symbol), pCurr, date)
        # if token.symbol == 'PSYOP':
        #     print('breakpoint')
        token.sell(amount, value=[0, 0] if symbol in self.pairs else [value, txFee])  # dont track p_l on base currencies
        self.findTokenBySymbol(str(feeCurrency), pCurr, date).sell(txFee)
        # print("New", token.symbol, "balance: ", str(token.balance), token.symbol)

### handle input args ###
argv = sys.argv[1:]
outfile = 'output.xlsx'
infile = '3ab3.csv'
mode = 'day'
try:
      opts, args = getopt.getopt(argv,"hm:i:o:",["ifile=","ofile="])
except getopt.GetoptError:
      print('py csvPL.py -m <[token] [day]> -i <inputfile> -o <outputfile>')
      sys.exit(2)

for opt, arg in opts:
    if opt == '-h':
        print('py csvPL.py -m <[token] [day]> -i <inputfile> -o <outputfile>')
        sys.exit()
    elif opt in ("-m", "--mode"):
        mode = arg
    elif opt in ("-i", "--ifile"):
        infile = arg
    elif opt in ("-o", "--ofile"):
        try:
            outfile = arg
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


df = pd.read_csv(infile, header=0, encoding_errors='replace')
parsed = df[['Timestamp', 'Transaction Type', 'Buy Amount', 'Buy Currency', 'Sell Amount', 'Sell Currency', 'Fee Amount', 'Fee Currency', 'Tx Hash']]

f=0  # flag to get from address on first iteration
addr = ''  # wallet address
normal_txs = []
for i, r in parsed.iterrows():
    date = str(parse(r[0]))[:10]
    # date = parse(r[0])
    txType = r[1]
    bAmount = r[2]
    bCurr = r[3]
    sAmount = r[4]
    sCurr = r[5]
    fAmount = r[6]
    fCurr = r[7]
    txHash = r[8]

    # process tx data
    if txType == 'trade':
        # some tx have multiple buy/sells split by \n
        bAmount = str(bAmount).split('\r\n')
        bCurr = str(bCurr).split('\r\n')
        sAmount = str(sAmount).split('\r\n')
        sCurr = str(sCurr).split('\r\n')

        if f==0:
            addr = es.get_transaction_by_hash(txHash)['from']
            normal_txs = es.get_transactions_by_address(addr)
            f=1

        for i in range(len(bCurr)):
            # if bCurr[i] == 'PSYOP':
            #     print('breakpoint')
            if sCurr[0] == 'ETH':
                tx = next((sub for sub in normal_txs if sub['hash']==txHash), None)
                sAmount[0] = w3.fromWei(tx['value'], 'ether')
            p.buy(bCurr[i], float(bAmount[i]), float(sAmount[i]) if i < len(sAmount) else 0, pCurr=sCurr[0], txFee=float(fAmount) if i==0 else 0, feeCurrency=fCurr, date=date)
        for i in range(len(sCurr)):
            if sCurr[i] == 'ETH':
                tx = next((sub for sub in normal_txs if sub['hash']==txHash), None)
                sAmount[i] = w3.fromWei(tx['value'], 'ether')
            p.sell(sCurr[i], float(sAmount[i]), float(bAmount[i]) if i < len(bAmount) else 0, pCurr=bCurr[0], date=date)

p_l_pertoken = []
p_l_perday = []
cum_pl = [[None], [0], [0]]  # cumulative p/l per pair [[pair], [p/l], [fees]]
daily_pl = [[None], [0], [0]]  # p/l per day, per pair (caclulated by date of purchase, not sell)
dates = [None]  # list of dates

def addDailyPL(token):
    if t.pair not in daily_pl[0]:  # make sure pair is in list of pairs
        daily_pl[0].append(t.pair)
        daily_pl[1].append(0)
        daily_pl[2].append(0)
    for i in daily_pl[0]:  # iterate through pairs
        if i == t.pair:
            idx = daily_pl[0].index(i)
            daily_pl[1][idx] += t.p_l
            daily_pl[2][idx] += t.fees

def printDailyPL():
    daily_pl[0].pop(0)  # remove none pair
    daily_pl[1].pop(0)
    daily_pl[2].pop(0)
    for i in daily_pl[0]:  # print all p/l pairs for the previous day
        idx = daily_pl[0].index(i)
        p_l_perday.append([dates[-1] if idx == 0 else '', daily_pl[1][idx], i, daily_pl[2][idx], 'ETH'])

for t in p.tokens:
    if t.pair not in cum_pl[0]:  # make sure pair is in list of pairs
        cum_pl[0].append(t.pair)
        cum_pl[1].append(0)
        cum_pl[2].append(0)
    for i in cum_pl[0]:  # iterate through pairs and accumulate p/l corresponding to that pair
        if i==t.pair:
            idx = cum_pl[0].index(i)
            cum_pl[1][idx] += t.p_l
            cum_pl[2][idx] += t.fees
            p_l_pertoken.append([t.symbol, t.balance, t.p_l, cum_pl[1][idx], t.pair, t.fees, cum_pl[2][idx], 'ETH'])

    date = t.dateSold
    if date in dates:
        addDailyPL(t)
    else:   # new date added. print previous day
        printDailyPL()
        daily_pl = [[None], [0], [0]]
        dates.append(date)
        addDailyPL(t)
printDailyPL()



if mode == 'token':
    pertoken = pd.DataFrame(p_l_pertoken, columns=['Symbol', 'Balance', 'P/L', 'Cumulative P/L', 'Token Pair', 'Fees', 'Cumulative Fees', 'Fee Pair'])
    pertoken.to_excel(outfile, encoding='utf-8')  # write to excel
    print(pertoken)

elif mode == 'day':
    perday = pd.DataFrame(p_l_perday, columns=['Date', 'P/L', 'Pair', 'Fees', 'Fee Pair'])
    perday.to_excel(outfile, encoding='utf-8')
    print(perday)
else:
    print("output mode not set pls contact Thomas")


print('done')




