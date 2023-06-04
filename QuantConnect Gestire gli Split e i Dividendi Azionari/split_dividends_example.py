### <summary>
### Basic template algorithm simply initializes the date range and cash. This is a skeleton
### framework you can use for designing an algorithm.
### </summary>
# region imports
from AlgorithmImports import *
import numpy as np


# endregion

class BasicTemplateAlgorithm(QCAlgorithm):
    '''Basic template algorithm simply initializes the date range and cash'''

    def Initialize(self):
        '''Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm. All algorithms must initialized.'''

        self.ticker = 'MSFT'
        self.raw_handling = True

        self.SetStartDate(2018, 5, 11)  # Data inizio
        self.SetEndDate(2018, 5, 22)  # Data Fine
        self.SetCash(10000)  # Capitale iniziale

        # Altri simboli qui: http://quantconnect.com/data
        self.AddEquity(self.ticker, Resolution.Daily)

        # Impostazione del metodo per gestire i dividendi
        # https://www.quantconnect.com/forum/discussion/508/update-dividends-splits-and-custom-price-normalization/p1
        if self.raw_handling:
            self.Securities[self.ticker].SetDataNormalizationMode(DataNormalizationMode.Raw)
        else:
            self.Securities[self.ticker].SetDataNormalizationMode(DataNormalizationMode.TotalReturn)

    def OnData(self, data):
        '''OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.

        Arguments:
            data: Slice object keyed by symbol containing the stock data
        '''
        if not self.Portfolio.Invested:
            self.SetHoldings(self.ticker, 1)

        for kvp in data.Dividends:  # aggiornare il dizionario degli eventi
            div_ticker = kvp.Key
            div_distribution = kvp.Value.Distribution
            div_total_value = div_distribution * self.Portfolio[self.ticker].Quantity
            self.Log(
                "{0} >> DIVIDEND >> {1} - ${2} - ${3}".format(self.Time, div_ticker, div_distribution, div_total_value))

        self.Log(
            "{0} >> SUMMARY >> {1} | Port Cash: {2} | Port Value: {3} | Holdings: {4} | Price {5}".format(self.Time,
                                                                                                          self.ticker,
                                                                                                          self.Portfolio.Cash,
                                                                                                          self.Portfolio.TotalPortfolioValue,
                                                                                                          self.Portfolio[
                                                                                                              self.ticker].Quantity,
                                                                                                          self.Portfolio[
                                                                                                              self.ticker].Price))