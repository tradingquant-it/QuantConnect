### <summary>
### Semplice strategia RSI che vuole fornire un esempio di un algoritmo
### usando un indicatore
### </summary>
# region imports
from AlgorithmImports import *
from datetime import timedelta


# endregion

class RSIAlgorithm(QCAlgorithm):

    # 1 - Aggiungere le FANG stocks (Facebook, Amazon, , Netflix, Google)
    # 2 - Ciclo attraverso le stocks
    # 3 - Aggiungere una equity per ogni stock
    # 3 - Creare un dizionario di indicatori

    def Initialize(self):
        '''Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm. All algorithms must initialized.'''

        # Impostazione parametri strategia
        self.SetStartDate(2016, 1, 1)  # Data inizio
        self.SetEndDate(2020, 1, 1)  # Data Fine
        self.SetCash(10000)  # Capitale iniziale

        RSI_Period = 14  # periodo del RSI
        self.RSI_OB = 75  # Livello overcomprato
        self.RSI_OS = 50  # Livello overvenduto
        self.Allocate = 0.20  # Percentuale di capitale allocato

        self.Equities = ["AAPL", "FB", "AMZN", "NFLX", "GOOG"]

        self.Indicators = dict()
        self.Charts = dict()
        self.Consolidators = dict()

        # Altri ticker sono disponibili in http://quantconnect.com/data
        for Symbol in self.Equities:
            self.Consolidators[Symbol] = dict()
            self.AddEquity(Symbol, Resolution.Daily)

            # Ogni Equity richiede il proprio consolidatore! Vedere:
            # https://www.quantconnect.com/forum/discussion/1936/multiple-consolidators/p1
            # https://www.quantconnect.com/forum/discussion/1587/multiple-symbol-indicator-values-in-consolidated-bar-handler/p1
            # ------------------------
            # Creare i consolidatori
            self.Consolidators[Symbol]['W1 Con'] = TradeBarConsolidator(timedelta(days=5))

            # Registrare gli Handlers
            self.Consolidators[Symbol]['W1 Con'].DataConsolidated += self.On_W1

            self.Indicators[Symbol] = dict()
            self.Indicators[Symbol]['RSI'] = dict()

            self.Indicators[Symbol]['RSI']['D'] = self.RSI(Symbol, RSI_Period)
            self.Indicators[Symbol]['RSI']['W'] = RelativeStrengthIndex(Symbol, RSI_Period)

            # Registrare gli indicatori con il titolo e il consolidatore
            self.RegisterIndicator(Symbol, self.Indicators[Symbol]['RSI']['W'], self.Consolidators[Symbol]['W1 Con'])

            # Aggiungere i consolidatori al subscription manager in modo
            # da ricevere gli aggiornamenti dal motore
            self.SubscriptionManager.AddConsolidator(Symbol, self.Consolidators[Symbol]['W1 Con'])

            self.Charts[Symbol] = dict()
            # Grafico RSI
            RSIChartName = Symbol + " RSI"
            self.Charts[Symbol]['RSI'] = Chart(RSIChartName, ChartType.Stacked)
            self.Charts[Symbol]['RSI'].AddSeries(Series("D1", SeriesType.Line))
            self.Charts[Symbol]['RSI'].AddSeries(Series("W1", SeriesType.Line))
            self.AddChart(self.Charts[Symbol]['RSI'])

            # Creare un grafico custom per il volume
            VolChartName = Symbol + " Volume"
            self.Charts[Symbol]['VOL'] = Chart(VolChartName, ChartType.Stacked)
            self.Charts[Symbol]['VOL'].AddSeries(Series('Buying Volume', SeriesType.Bar))
            self.Charts[Symbol]['VOL'].AddSeries(Series('Selling Volume', SeriesType.Bar))
            self.AddChart(self.Charts[Symbol]['VOL'])

        # Verifica che gli indicatori haano abbasta dati prima di iniziare il trading,
        # x5 è sufficiente per i dati settimanali
        self.SetWarmUp(RSI_Period * 5)

    def On_W1(self, sender, bar):
        '''
        This method will be called every time a new 30 minute bar is ready.

        bar = The incoming Tradebar. This is different to the data object in OnData()
        '''
        if self.IsWarmingUp: return

        Symbol = str(bar.get_Symbol())
        self.Plot(Symbol + ' RSI', 'W1', self.Indicators[Symbol]['RSI']['W'].Current.Value)

    def OnData(self, data):
        '''OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.

        Arguments:
            data: Slice object keyed by symbol containing the stock data
        '''
        if self.IsWarmingUp: return

        # Ciclo attraverso i simboli
        for Symbol in self.Equities:

            # aggiungere alias per facile lettura
            Close = data[Symbol].Close
            Volume = data[Symbol].Volume
            D1_RSI = self.Indicators[Symbol]['RSI']['D'].Current.Value
            W1_RSI = self.Indicators[Symbol]['RSI']['W'].Current.Value

            self.Debug("{}: Close: {} RSI: {}".format(Symbol, Close, D1_RSI))

            if data[Symbol].Close >= data[Symbol].Open:
                self.Plot(Symbol + " Volume", 'Buying Volume', Volume)
            else:
                self.Plot(Symbol + " Volume", 'Selling Volume', Volume)

            self.Plot(Symbol + ' RSI', 'D1', D1_RSI)

            # Determinare le condizioni di entrata e uscita
            Long_Cond1 = D1_RSI < self.RSI_OS
            Long_Cond2 = W1_RSI < self.RSI_OS
            Exit_Cond1 = D1_RSI > self.RSI_OB
            Exit_Cond2 = W1_RSI > self.RSI_OB

            if not self.Securities[Symbol].Invested:
                # Condizione Long
                if all([Long_Cond1, Long_Cond2]):
                    # Compra
                    self.SetHoldings(Symbol, self.Allocate)
            else:

                if all([Exit_Cond1, Exit_Cond2]):
                    # Vendi
                    self.Liquidate(Symbol)