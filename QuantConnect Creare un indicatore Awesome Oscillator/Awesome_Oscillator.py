import numpy as np
from collections import deque
from datetime import datetime


### <summary>
### Basic template algorithm simply initializes the date range and cash. This is a skeleton
### framework you can use for designing an algorithm.
### </summary>

class AwesomeOscillator:
    '''
    //@version=3
    study(title="Awesome Oscillator", shorttitle="AO")
    ao = sma(hl2,5) - sma(hl2,34)
    plot(ao, color = change(ao) <= 0 ? red : green, style=histogram)
    '''

    def __init__(self, period_fast=5, period_slow=34):
        self.Name = "Awesome Osc - {}, {}".format(period_fast, period_slow)
        self.Time = datetime.min
        self.Value = 0
        self.IsReady = False

        self.fast_sma_queue = deque(maxlen=period_fast)
        self.slow_sma_queue = deque(maxlen=period_slow)

    def __repr__(self):
        return "{0} -> IsReady: {1}. Time: {2}. Value: {3}".format(self.Name, self.IsReady, self.Time, self.Value)

    # metodo Update obbligatorio
    def Update(self, input):
        # Riempire le serie
        hl2 = (input.High + input.Low) / 2
        self.fast_sma_queue.appendleft(hl2)
        self.slow_sma_queue.appendleft(hl2)

        # Calcolare le SMA
        fast_count = len(self.fast_sma_queue)
        fast_sma = sum(self.fast_sma_queue) / fast_count

        slow_count = len(self.slow_sma_queue)
        slow_sma = sum(self.slow_sma_queue) / slow_count

        self.Value = fast_sma - slow_sma

        self.Time = input.EndTime
        self.IsReady = slow_count == self.slow_sma_queue.maxlen


class BasicTemplateAlgorithm(QCAlgorithm):
    '''Basic template algorithm simply initializes the date range and cash'''

    def Initialize(self):
        '''Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm. All algorithms must initialized.'''

        self.SetStartDate(2018, 1, 1)  # Imposta la data inizio
        self.SetEndDate(2019, 1, 1)  # Imposta la data fine
        self.SetCash(100000)  # Imposta il capitale della strategia
        # Find more symbols here: http://quantconnect.com/data
        self.AddEquity("SPY", Resolution.Daily)

        self.AO = AwesomeOscillator()
        self.RegisterIndicator("SPY", self.AO, Resolution.Daily)

        # Creare il grafico dell'indicatore
        AOChart = Chart("Awesome", ChartType.Stacked)
        AOChart.AddSeries(Series('AO', SeriesType.Line))

    def OnData(self, data):
        '''OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.

        Arguments:
            data: Slice object keyed by symbol containing the stock data
        '''

        self.Debug(self.AO)

        if not self.AO.IsReady: return

        self.Plot('Awesome', 'AO', self.AO.Value)