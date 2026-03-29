
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
import yfinance as yf 

def calculate_vwap(df):
    df['TP'] = (df['High'] + df['Low'] + df['Close']) / 3
    tp_vol = df['TP'] * df['Volume']
    df['VWAP'] = tp_vol.cumsum() / df['Volume'].cumsum()
    return df  

def calculate_atr(df, period=14):
    high_low = df['High'] - df['Low']
    high_pc = abs(df['High'] - df['Close'].shift(1))
    low_pc = abs(df['Low'] - df['Close'].shift(1))
    df['TR'] = pd.concat([high_low, high_pc, low_pc], axis=1).max(axis=1)
    df['ATR'] = df['TR'].rolling(window=period).mean()
    return df

def calculate_supertrend(df, period=10, multiplier=3):
    df = calculate_atr(df, period)
    df['ST_Upper'] = ((df['High'] + df['Low']) / 2) + (multiplier * df['ATR'])
    df['ST_Lower'] = ((df['High'] + df['Low']) / 2) - (multiplier * df['ATR'])
    return df 

def calculate_adx(df, period=14):
    df = calculate_atr(df, period)
    up_move = df['High'] - df['High'].shift(1)
    down_move = df['Low'].shift(1) - df['Low']
    
    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)
    
    # Smooth DI values
    plus_di = 100 * (pd.Series(plus_dm, index=df.index).rolling(period).mean() / df['ATR'])
    minus_di = 100 * (pd.Series(minus_dm, index=df.index).rolling(period).mean() / df['ATR'])
    
    dx = 100 * (abs(plus_di - minus_di) / (plus_di + minus_di))
    df['ADX'] = dx.rolling(period).mean()
    return df 



ticker = "^NSEI"
stock_data = yf.download(ticker, start='2024-01-01')


stock_data.columns = stock_data.columns.get_level_values(0)

stock_data = calculate_vwap(stock_data)
stock_data = calculate_adx(stock_data)
stock_data = calculate_supertrend(stock_data)


fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

ax1.plot(stock_data['Close'], color='red', label='Nifty 50 Price', linewidth=1.5)
ax1.plot(stock_data['VWAP'], color='blue', label='VWAP', linestyle='--')
ax1.plot(stock_data['ST_Lower'], color='green', label='Supertrend Support', alpha=0.5)
ax1.set_title(f'Analysis for {ticker}')
ax1.legend()

ax2.plot(stock_data['ADX'], color='black', label='ADX')
ax2.axhline(25, color='purple', linestyle=':', label='Strong Trend (25)')
ax2.legend()

plt.tight_layout()
plt.show()



