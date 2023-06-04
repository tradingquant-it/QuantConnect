### <summary>
### Semplice strategia RSI che vuole fornire un esempio di un algoritmo
### usando un indicatore
### </summary>
# region imports
from AlgorithmImports import *


# endregion

class RSIAlgorithm(QCAlgorithm):

    def Initialize(self):
        '''Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm. All algorithms must initialized.'''

        # Impostazione parametri strategia
        self.SetStartDate(2012, 1, 1)  # Data inizio
        self.SetEndDate(2020, 1, 1)  # Data Fine
        self.SetCash(10000)  # Capitale iniziale

        RSI_Period = 14  # periodo del RSI
        self.RSI_OB = 60  # Livello overcomprato
        self.RSI_OS = 40  # Livello overvenduto
        self.Allocate = 0.25  # Percentuale di capitale allocato

        # Altri ticker sono disponibili in http://quantconnect.com/data
        self.AddEquity("AAPL", Resolution.Daily)

        self.RSI_Ind = self.RSI("AAPL", RSI_Period)

        # Verifica che ci siano abbastanza dati per calcolare l'indicatore prima del trading...
        self.SetWarmUp(RSI_Period)

        # Grafico il RSI
        self.PlotIndicator("RSI", self.RSI_Ind)

        # Creazione di un grafico custom per i volumi
        VolChart = Chart("Volume", ChartType.Stacked)
        VolChart.AddSeries(Series('Buying Volume', SeriesType.Bar))
        VolChart.AddSeries(Series('Selling Volume', SeriesType.Bar))
        self.AddChart(VolChart)

    def OnData(self, data):
        '''OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.

        Arguments:
            data: Slice object keyed by symbol containing the stock data
        '''
        if data["AAPL"] is not None:
            if data["AAPL"].Close >= data["AAPL"].Open:
                self.Plot('Volume', 'Buying Volume', data["AAPL"].Volume)
            else:
                self.Plot('Volume', 'Selling Volume', data["AAPL"].Volume)

        # Verifica se siamo a mercato
        if not self.Portfolio.Invested:
            # Se siamo flat verifichiamo l'RSI
            if self.RSI_Ind.Current.Value < self.RSI_OS:
                # Compriamo Apple
                self.SetHoldings("AAPL", self.Allocate)
        else:
            if self.RSI_Ind.Current.Value > self.RSI_OB:
                # Vendiamo Apple
                self.Liquidate("AAPL")