import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf

# 마녀공장 (MNYC)의 데이터 불러오기
ticker = '439090.KQ'  # 한국 주식의 티커는 다르게 표기됩니다.
data = yf.download(ticker, start='2020-01-01', end='2024-01-01')

# RSI 계산
window_length = 14
close = data['Close']
delta = close.diff()
gain = (delta.where(delta > 0, 0)).fillna(0)
loss = (-delta.where(delta < 0, 0)).fillna(0)
avg_gain = gain.rolling(window=window_length).mean()
avg_loss = loss.rolling(window=window_length).mean()
rs = avg_gain / avg_loss
rsi = 100 - (100 / (1 + rs))

# MACD, Signal Line, MACD 오실레이터 계산
ema_12 = close.ewm(span=12, adjust=False).mean()
ema_26 = close.ewm(span=26, adjust=False).mean()
macd = ema_12 - ema_26
signal_line = macd.ewm(span=9, adjust=False).mean()
macd_hist = macd - signal_line

# Plotting
fig, (ax1, ax2, ax3) = plt.subplots(3, figsize=(14, 10), sharex=True)

ax1.plot(data.index, close, label='Close Price')
ax1.set_title('Close Price')
ax1.legend()

ax2.plot(data.index, rsi, label='RSI')
ax2.axhline(70, color='r', linestyle='--')
ax2.axhline(30, color='g', linestyle='--')
ax2.set_title('RSI')
ax2.legend()

ax3.plot(data.index, macd, label='MACD')
ax3.plot(data.index, signal_line, label='Signal Line')
ax3.bar(data.index, macd_hist, label='MACD Histogram', color='gray')
ax3.set_title('MACD')
ax3.legend()

plt.show()
