import backtrader as bt
import yfinance as yf

class SmaCross(bt.SignalStrategy):
    def __init__(self):
        sma1, sma2 = bt.ind.SMA(period=50), bt.ind.SMA(period=200)
        crossover = bt.ind.CrossOver(sma1, sma2)
        self.signal_add(bt.SIGNAL_LONG, crossover)

cerebro = bt.Cerebro()
cerebro.addstrategy(SmaCross)

data = bt.feeds.PandasData(dataname=yf.download('AAPL', '2020-01-01', '2023-01-01'))
cerebro.adddata(data)
cerebro.run()
cerebro.plot()
