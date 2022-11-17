import numpy as np
import pandas as pd
from dateutil.parser import parse
from datetime import datetime
from objects import Portfolio2
import sys

# total arguments
n = len(sys.argv)
infile = sys.argv[1]
outfile = 'output.xlsx'
try:
    outfile = sys.argv[2]
except:
    print('No output file specified, sending it to output.xlsx')

p = Portfolio2(None)
df = pd.read_csv(infile, header=0, usecols=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,21])
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
        bAmount = str(bAmount).split('\n')
        bCurr = bCurr.split('\n')
        sAmount = str(sAmount).split('\n')
        sCurr = sCurr.split('\n')

        for i in range(len(bCurr)):
            p.buy(bCurr[i], float(bAmount[i]), value=float(sAmount[0]), txFee=float(fAmount) if i==0 else 0, feeCurrency=fCurr)
        for i in range(len(sCurr)):
            p.sell(sCurr[i], float(sAmount[i]), value=float(bAmount[0]))

p_l = []
for t in p.tokens:
    p_l.append([t.symbol, t.balance, t.p_l, t.pair])


pl_percoin = pd.DataFrame(p_l, columns=['Symbol', 'Balance', 'P/L', 'Pair'])

pl_percoin.to_excel(outfile)
print('done')




