import numpy as np
from BLT import BasicTemplateLibrary
from SimpFunc import Subtract

### <summary>
### Basic template algorithm simply initializes the date range and cash. This is a skeleton
### framework you can use for designing an algorithm.
### </summary>

class BasicTemplateAlgorithm(QCAlgorithm):
    '''Basic template algorithm simply initializes the date range and cash'''

    def Initialize(self):
        '''Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm. All algorithms must initialized.'''

        self.SetStartDate(2013, 10, 7)  # Set Start Date
        self.SetEndDate(2013, 10, 11)  # Set End Date
        self.SetCash(100000)  # Set Strategy Cash
        self.Ticker = "SPY"
        # Più simboli su: http://quantconnect.com/data
        self.AddEquity(self.Ticker, Resolution.Daily)

    def OnData(self, data):
        '''OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.

        Arguments:
            data: Slice object keyed by symbol containing the stock data
        '''

        # Ottenere i dati OHLC
        if data.ContainsKey(self.Ticker) and data.HasData:
            O = data[self.Ticker].Open
            H = data[self.Ticker].High
            L = data[self.Ticker].Low
            C = data[self.Ticker].Close
            P = data[self.Ticker].Price

            HmL = Subtract(H, L)

            self.Log(">> High: {} Low: {} | High - Low: {}".format(H, L, HmL))

        if not self.Portfolio.Invested:
            self.SetHoldings(self.Ticker, 1)