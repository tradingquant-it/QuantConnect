### <summary>
### Simple RSI Strategy intended to provide a minimal algorithm example using
### one indicator
### </summary>

# region imports
from AlgorithmImports import *
from System.Drawing import Color


# endregion

class RSIAlgorithm(QCAlgorithm):

    def Initialize(self):
        '''Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm. All algorithms must initialized.'''

        # Impostazione dei parametri della strategia
        self.SetStartDate(2014, 12, 1)  # Data Inizio
        self.SetEndDate(2015, 1, 1)  # Data Fine
        self.SetCash(10000)  # Capitale Iniziale

        self.Equities = ["AAPL"]

        self.HK = dict()  # Creare un dizionario per memorizzare gli indicatori HK

        for Equity in self.Equities:
            # Altri simbolo su: http://quantconnect.com/data
            self.AddEquity(Equity, Resolution.Daily)
            self.HK[Equity] = self.HeikinAshi(Equity, Resolution.Daily)

            # Suggerimento 1: Grafico a linea
            # --------------------------------------
            # Nota: Questo è stato commentato in quanto
            #       siamo limitati a 10 serie per backtest.
            #       Per testare, decommenta le righe
            #       sottostanti e poi commenta il
            #       suggerimento 3 o 4.
            # ---------------------------------------
            # self.PlotIndicator(
            #    Equity + " - Line",
            #    self.HK[Equity].Open,
            #    self.HK[Equity].High,
            #    self.HK[Equity].Low,
            #    self.HK[Equity].Close
            #    )

            # Suggerimento 2: Grafico a candele
            # ---------------------------------------
            CandChart = Chart(Equity + "- Candle", ChartType.Stacked)
            CandChart.AddSeries(Series('Heikinashi', SeriesType.Candle))
            self.AddChart(CandChart)

            # Suggerimento 3: Grafico Scatter
            # ---------------------------------------
            ScatPlot = Chart(Equity + "- X", ChartType.Stacked)
            ScatPlot.AddSeries(Series('Open', SeriesType.Scatter, '$', Color.Black, ScatterMarkerSymbol.Circle))
            ScatPlot.AddSeries(Series('High', SeriesType.Scatter, '$', Color.Green, ScatterMarkerSymbol.Triangle))
            ScatPlot.AddSeries(Series('Low', SeriesType.Scatter, '$', Color.Red, ScatterMarkerSymbol.TriangleDown))
            ScatPlot.AddSeries(Series('Close', SeriesType.Scatter, '$', Color.Black, ScatterMarkerSymbol.Square))
            self.AddChart(ScatPlot)

            # Suggerimento 4: Grafico Misto
            # ---------------------------------------
            SAPlot = Chart(Equity + "- Mix", ChartType.Stacked)
            SAPlot.AddSeries(Series('Price', SeriesType.Line, "$", Color.Black))
            SAPlot.AddSeries(Series('Bullish', SeriesType.Scatter, "$", Color.Green, ScatterMarkerSymbol.Circle))
            SAPlot.AddSeries(Series('Bearish', SeriesType.Scatter, "$", Color.Red, ScatterMarkerSymbol.Circle))
            SAPlot.AddSeries(Series('Neutral', SeriesType.Scatter, "$", Color.Black, ScatterMarkerSymbol.Circle))
            SAPlot.AddSeries(Series('High', SeriesType.Scatter, '$', Color.Black, ScatterMarkerSymbol.Triangle))
            SAPlot.AddSeries(Series('Low', SeriesType.Scatter, '$', Color.Black, ScatterMarkerSymbol.TriangleDown))
            self.AddChart(SAPlot)

    def OnData(self, data):
        '''OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.

        Arguments:
            data: Slice object keyed by symbol containing the stock data
        '''

        for Equity in self.Equities:

            # Alias
            # -----------------------------------------------------------------

            # Heikin
            HK_O = self.HK[Equity].Open.Current.Value
            HK_H = self.HK[Equity].High.Current.Value
            HK_L = self.HK[Equity].Low.Current.Value
            HK_C = self.HK[Equity].Close.Current.Value
            HK_P = self.HK[Equity].Current.Price

            # OHLC
            O = data[Equity].Open
            H = data[Equity].High
            L = data[Equity].Low
            C = data[Equity].Close
            P = data[Equity].Price

            # -----------------------------------------------------------------

            # Heikin Sentiment
            # ---------------------------------------
            if HK_O < HK_C:
                HK_S = "Bull"
            elif HK_O > HK_C:
                HK_S = "Bear"
            else:
                HK_S = "Neut"

            # Option 2: Grafico a Candele
            # ---------------------------------------
            self.Plot(Equity + "- Candle", 'Heikinashi', HK_P)

            # Option 3: Grafico Scatter
            # ---------------------------------------
            self.Plot(Equity + "- X", 'Open', HK_O)
            self.Plot(Equity + "- X", 'High', HK_H)
            self.Plot(Equity + "- X", 'Low', HK_L)
            self.Plot(Equity + "- X", 'Close', HK_C)

            # Option 4: Grafico Misto
            # ---------------------------------------
            self.Plot(Equity + "- Mix", 'Price', HK_P)
            self.Plot(Equity + "- Mix", 'High', HK_H)
            self.Plot(Equity + "- Mix", 'Low', HK_L)
            if HK_S == "Bull":
                self.Plot(Equity + "- Mix", 'Bullish', HK_P)
            elif HK_S == "Bear":
                self.Plot(Equity + "- Mix", 'Bearish', HK_P)
            else:
                self.Plot(Equity + "- Mix", 'Neutral', HK_P)

            # Logging
            # -----------------------------------------------------------------

            self.Log("{0} OHLC   >> O: {1} H: {2} L:{3}, C:{4} | Price: {5}".format(Equity, O, H, L, C, P))
            self.Log("{0} Heikin >> O: {1} H: {2} L:{3}, C:{4} | Price: {5} | Sentiment: {6}".format(Equity, HK_O, HK_H,
                                                                                                     HK_L, HK_C, HK_P,
                                                                                                     HK_S))

            # Criteri Entrata / Uscita
            # -----------------------------------------------------------------

            # Controlo se siamo a mercato
            if not self.Portfolio.Invested:
                # Controlo se il HK sentiment è bullish
                if HK_S == "Bull":
                    self.SetHoldings(Equity, 0.5)
            else:
                if HK_S == "Bear":
                    self.Liquidate(Equity)