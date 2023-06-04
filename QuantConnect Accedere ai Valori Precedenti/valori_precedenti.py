### <summary>
### Simple RSI Strategy intended to provide a minimal algorithm example using
### one indicator
### </summary>
# region imports
from AlgorithmImports import *
from decimal import *


# endregion

class RSIAlgorithm(QCAlgorithm):

    def Initialize(self):
        '''Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm. All algorithms must initialized.'''

        # Parametri della strategia
        self.SetStartDate(2018, 1, 1)  # Set Start Date
        self.SetEndDate(2018, 1, 10)  # Set End Date
        self.SetCash(10000)  # Set Strategy Cash

        RSI_Period = 14  # RSI Look back period
        self.RSI_OB = 60  # RSI Overbought level
        self.RSI_OS = 40  # RSI Oversold level
        self.Allocate = 0.25  # Percentage of captital to allocate

        # Altri simboli disponibili su: http://quantconnect.com/data
        self.AddEquity("AAPL", Resolution.Daily)

        self.RSI_Ind = self.RSI("AAPL", RSI_Period)

        # Creare la finestra mobile
        self.tradeBarWindow = RollingWindow[TradeBar](5)  # Store the last 5 values
        self.rsiWindow = RollingWindow[float](10)  # Store the last 10 values

        # Assicurarsi che l'indicatore ha sufficienti dati prima di iniziare il trading
        self.SetWarmUp(RSI_Period)

    def OnData(self, data):
        '''OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.

        Arguments:
            data: Slice object keyed by symbol containing the stock data
        '''

        # Aggiornamento della finestra mobile
        self.tradeBarWindow.Add(data["AAPL"])
        self.rsiWindow.Add(self.RSI_Ind.Current.Value)

        # Aspettare che la finestra sia pronta
        if not (self.tradeBarWindow.IsReady and self.rsiWindow.IsReady): return

        self.Debug('{} Current RSI: {}, Prev RSI: {}'.format(self.Time, round(self.rsiWindow[0], 2),
                                                             round(self.rsiWindow[1], 2)))
        self.Debug('{} Current Close: {}, Prev Close: {}'.format(self.Time, round(self.tradeBarWindow[0].Close, 2),
                                                                 round(self.tradeBarWindow[1].Close, 2)))