### <summary>
### Semplice strategia RSI che vuole fornire un esempio di un algoritmo
### usando un indicatore
### </summary>
# region imports
from AlgorithmImports import *
from datetime import timedelta


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

        # Creare i consolidatori
        W1_Con = TradeBarConsolidator(timedelta(days=5))

        # Registrare gli Handlers
        W1_Con.DataConsolidated += self.On_W1

        # Creare gli indicatori
        self.RSI_Ind = self.RSI("AAPL", RSI_Period)
        self.W1_RSI = RelativeStrengthIndex("AAPL", RSI_Period)

        # Registrare gli indicatori per l'asset e il consolidatore
        self.RegisterIndicator("AAPL", self.W1_RSI, W1_Con)

        # Aggiungere i consolidatori al manager delle sottoscrizioni
        # in modo da ricevere aggiornamente dal motore
        self.SubscriptionManager.AddConsolidator("AAPL", W1_Con)

        # Verifica che gli indicatori haano abbasta dati prima di iniziare il trading,
        # x5 è sufficiente per i dati settimanali
        self.SetWarmUp(RSI_Period * 5)

        # Grafico il RSI
        RSIChart = Chart("RSI", ChartType.Stacked)
        RSIChart.AddSeries(Series("D1", SeriesType.Line))
        RSIChart.AddSeries(Series("W1", SeriesType.Line))
        self.AddChart(RSIChart)

        # Creazione di un grafico custom per i volumi
        VolChart = Chart("Volume", ChartType.Stacked)
        VolChart.AddSeries(Series('Buying Volume', SeriesType.Bar))
        VolChart.AddSeries(Series('Selling Volume', SeriesType.Bar))
        self.AddChart(VolChart)

    def On_W1(self, sender, bar):
        '''
        This method will be called every time a new 30 minute bar is ready.

        bar = The incoming Tradebar. This is different to the data object in OnData()
        '''
        self.Plot('RSI', 'W1', self.W1_RSI.Current.Value)

    def OnData(self, data):
        '''OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.

        Arguments:
            data: Slice object keyed by symbol containing the stock data
        '''

        self.Plot('RSI', 'D1', self.RSI_Ind.Current.Value)

        if data["AAPL"] is not None:
            if data["AAPL"].Close >= data["AAPL"].Open:
                self.Plot('Volume', 'Buying Volume', data["AAPL"].Volume)
            else:
                self.Plot('Volume', 'Selling Volume', data["AAPL"].Volume)

        # Assicura che non siamo in warm up
        if self.IsWarmingUp: return

        # Determina le condizioni di entrata e uscita
        long_cond1 = self.RSI_Ind.Current.Value < self.RSI_OS
        long_cond2 = self.W1_RSI.Current.Value < self.RSI_OS
        exit_cond1 = self.RSI_Ind.Current.Value > self.RSI_OB
        exit_cond2 = self.W1_RSI.Current.Value > self.RSI_OB

        # Verifica se siamo a mercato
        if not self.Portfolio.Invested:
            # Se siamo flat verifichiamo l'RSI
            if all([long_cond1, long_cond2]):
                # Compriamo Apple
                self.SetHoldings("AAPL", self.Allocate)
        else:
            if all([exit_cond1, exit_cond2]):
                # Vendiamo Apple
                self.Liquidate("AAPL")