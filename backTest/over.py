import pandas_datareader as web
from datetime import datetime
import pandas as pd
import numpy as np
#from matplotlib import pyplot
import matplotlib.pyplot as plt
import yfinance as yf

start = datetime(2013, 1, 1)

end = datetime(2023, 1, 31)

#item_code = '035420'        # 네이버

item_code = '005930'        # 삼성전자

#item_code = '005380'        # 현대자동차

#item_code = '006400'        # 삼성SDI

# item_code = '035720'        # 카카오

#item_code = '004170'        #신세계

#item_code = '000660'        #하이닉스

#item_code = '007575'        #일양약품우

#item_code = '028300'        #에이치엘비

#item_code = '068270'        #셀트리온

#item_code = '253280'        #KBSTAR 헬스케어

#item_code = '017180'        # 넥센

#item_code = '019170'


# df = web.get_data_yahoo('AAPL', start, end)
df = yf.download('AAPL', start , end)
# df = web.DataReader(item_code + '.KS', 'yahoo', start, end)

# df = web.DataReader('ETH-USD', 'yahoo', start, end)
# df = web.DataReader('BTC-USD', 'yahoo', start, end)

#df = web.DataReader('TSLA', 'yahoo', start, end)

#print('Code : ' + str(item_code) )

fee = 0.0032        #수수료 + 세금 + 슬립피지
#fee = 0.002

print('Fee :' + str(fee * 100) + '%')

print(df)

#df['Range'] = (df['High'] - df['Low']) * K
#df['Target'] = df['Open'] + df['Range'].shift(1)

df['Target'] = df['High'].shift(1)

df['Sell'] = df['Open'].shift(-1)           #매도가

#df['Target'] = np.where(df['Open'] > df['High'].shift(1), df['Open'], df['High'].shift(1))


df['ROR'] = np.where(df['High'] > df['Target'], df['Sell'] / df['Target'] - fee, 1)


df['HPR'] = df['ROR'].cumprod()

df['HPR2'] = df['Close']/df.iloc[0]['Close']

df['DD'] = (df['HPR'].cummax() - df['HPR']) / df['HPR'].cummax() * 100

df['DD2'] = (df['HPR2'].cummax() - df['HPR2']) / df['HPR2'].cummax() * 100

date = (df.index[-1] - df.index[0]).days

print('-------------------------------')
print('Holding')
print('-------------------------------')

print("MDD: ", df['DD2'].max())
print("HPR: ", df['HPR2'][-2])

cagr2 = round(((df['HPR2'][-2]/1) ** (1/(date/365))-1) * 100, 1)

print("CAGR: ", str(cagr2) + '%'  )

print('-------------------------------')
print('Breakthrough strategy')
print('-------------------------------')

print("MDD: ", df['DD'].max())

print("HPR: ", df['HPR'][-2])




cagr = round(((df['HPR'][-2]/1) ** (1/(date/365))-1) * 100, 1)

print("CAGR: ", str(cagr) + '%'  )

win = np.count_nonzero(df['ROR'] > 1)

lose = np.count_nonzero(df['ROR'] < 1)

POV = round(win/(win + lose) * 100, 1)

print("Percentages of Victories : %d%%(Win:%d, Lose:%d)"%(POV,win,lose))

'''
df['HPR'].plot(color='#ff0000')
pyplot.grid()
pyplot.legend()
pyplot.title('Graph')
pyplot.xlabel('year')
pyplot.ylabel('hpr')
pyplot.show()
'''

plt.subplot(211)
plt.plot(df['HPR2'])


#plt.xlabel('year')

plt.subplot(212)
plt.plot(df['HPR'])

plt.show()

df.to_excel("data.xlsx")



