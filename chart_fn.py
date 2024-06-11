import FinanceDataReader as fdr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os, datetime, glob
import plotly.graph_objects as go

def mdd_fn(df):
    df = df[['Close']].copy()

    def return_fn(df): 
        return df['Close'].pct_change().fillna(0)

    def cum_return_fn(df_return):
        return (1 + df_return).cumprod()

    df['return'] = return_fn(df)
    df['cum_return'] = cum_return_fn(df['return'])
    df['max_cum_return'] = df['cum_return'].cummax()
    df['drawdown'] = df['cum_return'] / df['max_cum_return'] - 1
    
    mdd = df['drawdown'].min()

    list_info = []

    max_close_value = df['Close'].max()
    min_close_value = df['Close'].min()

    print('Max Close Value: ', max_close_value)
    print('Min Close Value: ', min_close_value)
    
    df_max_close = df[df['drawdown'] == 0].copy()
    df_max_close.loc[df.index[len(df)-1]] = 0

    period = df_max_close.index[1:] - df_max_close.index[:-1]
    mdd_days = period.days
    max_period = mdd_days.max()
    max_period_idx = mdd_days.argmax()

    print('Max Drawdown Period: ', max_period)
    print('Date: ', df_max_close.index[:-1][max_period_idx].date(), end=' ~ ')
    print(df_max_close.index[1:][max_period_idx].date())

    list_info.append(max_close_value)
    list_info.append(min_close_value)
    list_info.append(round(mdd, 4))
    list_info.append(df_max_close.index[:-1][max_period_idx].date())
    list_info.append(df_max_close.index[1:][max_period_idx].date())
    list_info.append(max_period)
    
    return df, list_info

def macdOscillator_fn(df, short_N=9, long_N=26, signal_N=13):
    df = df[['Close']].copy() 
    
    df['Short'] = df['Close'].ewm(span=short_N, adjust=False).mean()
    df['Long'] = df['Close'].ewm(span=long_N, adjust=False).mean()
    
    df['MACD'] = df['Short'] - df['Long']
    df['Signal'] = df['MACD'].ewm(span=signal_N, adjust=False).mean()
    df['MACD Oscillator'] = df['MACD'] - df['Signal']
    
    return df[['MACD', 'Signal', 'MACD Oscillator']]

def stockDataReader_fn(market, stockName, startDate = None, endDate = None):
    docPosition = "market_data/"
    today = datetime.date.today()
    
    fileName = docPosition + "{}-{}.csv".format(market, today)
    if os.path.isfile(fileName) == False:
        raise Exception('do not exist market data file')
    df = pd.read_csv(fileName)
    
    if stockName in df['Name'].values: # Name || Symbol
        code = df[df['Name'] == stockName]['Code'].values[0]
    elif stockName in df['Symbol'].values:
        code = stockName
    else:
        print('do not exist stock name')
        raise Exception('do not exist market data code')

    stockData = fdr.DataReader(code, start=startDate, end=endDate)
    return stockData

def stockDataReader_fn(stockName, startDate = None, endDate = None):
    markets = ['krx', 'kospi','kosdaq','konex', 'krx-marcap', 'krx-desc', 'kospi-desc', 'kosdaq-desc', 'konex-desc', 'krx-delisting', 'krx-administrative', 'krx-marcap', 'nasdaq', 'nyse', 'amex', 'sse', 'szse', 'hkex', 'tse', 'hose', 's&p500', 'etf/kr']
    docPosition = "market_data/"
    today = datetime.date.today()
    
    for market in markets:
        marketName = market
        if market.find('/'):
            marketName = market.replace('/', '-')
        fileName = docPosition + "{}-{}.csv".format(marketName, today)
        if os.path.isfile(fileName) == False:
            raise Exception('do not exist market data file')
        df = pd.read_csv(fileName)
        
        # check df has column Name and Symbol
        if 'Name' in df.columns and stockName in df['Name'].values: # Name || Symbol
            code = df[df['Name'] == stockName]['Code'].values[0]
        elif 'Symbol' in df.columns and stockName in df['Symbol'].values:
            code = stockName
            
    if code == None:
        print('do not exist stock name')
        raise Exception('do not exist market data code')

    stockData = fdr.DataReader(code, start=startDate, end=endDate)
    return stockData

def rsi_fn(df, rsi_period=14):
    df = df.copy()
    df['avgGain'] = df['Close'].diff()
    df['avgLoss'] = df['Close'].diff()
    df['avgGain'][df['avgGain'] < 0] = 0
    df['avgLoss'][df['avgLoss'] > 0] = 0
    df['avgGain'] = df['avgGain'].rolling(window=rsi_period).mean() # EWM -> 지수이동평균 / rolling -> 이동평균 | 차이: 지수이동평균은 최근값에 가중치를 더 둠
    df['avgLoss'] = df['avgLoss'].rolling(window=rsi_period).mean()
    df['RS'] = df['avgGain'].abs() / df['avgLoss'].abs()
    df['RSI'] = 100 - (100 / (1 + df['RS']))
    
    def print_rsi():
        plt.figure(figsize=(15, 5))
        plt.plot(df.index, df['RSI'], label='RSI')
        plt.axhline(80, color='b', linestyle='--')
        plt.axhline(70, color='r', linestyle='--')
        plt.axhline(30, color='g', linestyle='--')
        plt.legend()
        plt.show()
        
    # print_rsi()
    return df

def todayMarketData():
    # today Stock List
    markets = ['krx', 'kospi','kosdaq','konex', 'krx-marcap', 'krx-desc', 'kospi-desc', 'kosdaq-desc', 'konex-desc', 'krx-delisting', 'krx-administrative', 'krx-marcap', 'nasdaq', 'nyse', 'amex', 'sse', 'szse', 'hkex', 'tse', 'hose', 's&p500', 'etf/kr']
    docPosition = "market_data/"
    today = datetime.date.today()
    
    for market in markets:
        marketName = market
        if market.find('/'):
            marketName = market.replace('/', '-')
        
        fileName = docPosition + "{}-{}.csv".format(marketName, today)
        if os.path.isfile(fileName) == False:
            try:
                if marketName == 'etf-kr':
                    for file in glob.glob(docPosition + marketName + "-[0-9]*"):
                        print(f'delete file {file}')
                        os.remove(file)
                
                for file in glob.glob(docPosition + market + "-[0-9]*"):
                    print(f'delete file {file}')
                    os.remove(file)
            except FileNotFoundError:
                print(f'file not found')
            except PermissionError:
                print(f'permission denied')
            
            df = fdr.StockListing(market=market)
            print(fileName)
            df.to_csv(fileName)

def plot_volume(df):
    volume = go.Bar(x=df.index, y=df['Volume'], name='Volume')
    fig = go.Figure(volume)
    return fig
