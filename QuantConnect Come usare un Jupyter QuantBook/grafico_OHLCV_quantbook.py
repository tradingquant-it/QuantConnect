import mplfinance as mpf

history = qb.History(qb.Securities.Keys, 30, Resolution.Daily)

ohlc = history.loc["SPY"]

ohlc = ohlc[['open', 'high', 'low', 'close', 'volume']]
ohlc.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

mpf.plot(ohlc, type='candlestick')