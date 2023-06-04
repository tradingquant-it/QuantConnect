import numpy as np

###
# All-Weather Portfolio
# ---------------------------------------------
# Strategy Author: Ray Dalio
# Source: Tony Robbins / Money, master the game
# ----------------------------------------------
###
class BasicTemplateAlgorithm(QCAlgorithm):
    '''Basic template algorithm simply initializes the date range and cash'''

    def Initialize(self):
        '''
        Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm.
        All algorithms must initialized.
        '''

        self.SetStartDate(2011, 1, 1)  # Imposto data inizio
        self.SetEndDate(2019, 1, 1)  # Imposto data fine
        self.SetCash(100000)  # Imposto capitale iniziale

        # Gestione dividendi
        self.raw_handling = True

        # Simulazione del PAC dei risparmi per ogni periodo
        self.savings_on = False
        self.savings_amt = 1000

        # Non effettuare il pca al primo ribilanciamento dopo l'esecuzione dell'algoritmo
        self.first_rebalance = True

        # Dizionario degli asset e dei pesi
        # può essere ampliato con altri ETF
        self.all_weather = {
            "Equity 1": {
                "Ticker": "VOO",  # Vanguard S&P 500 ETF
                "Weight": 0.15,
            },
            "Equity 2": {
                "Ticker": "VEA",  # Vanguard FTSE Developed Markets ETF
                "Weight": 0.15,
            },

            "Bonds Med-Term": {
                "Ticker": "IEF",  # iShares 7-10 Year Treasury Bond ETF
                "Weight": 0.15,
            },

            "Bonds Long-Term": {
                "Ticker": "TLT",  # iShares 20+ Year Treasury Bond ETF
                "Weight": 0.4,
            },
            "Commodity 1": {
                "Ticker": "GLD",  # SPDR Gold Trust
                "Weight": 0.075,
            },
            "Commodity 2": {
                "Ticker": "USO",  # United States Oil Fund
                "Weight": 0.075,
            },

        }

        # Imposta la simulazione del broker IB
        self.SetBrokerageModel(BrokerageName.InteractiveBrokersBrokerage)

        # Aggiunge gli ETF
        # ---------------
        for key, asset in self.all_weather.items():
            self.AddEquity(asset["Ticker"], Resolution.Daily)

            # Imposta il metodo per gestire i dividenti
            # ----------------------------
            # https://www.quantconnect.com/forum/discussion/508/update-dividends-splits-and-custom-price-normalization/p1
            if self.raw_handling:
                self.Securities[asset["Ticker"]].SetDataNormalizationMode(DataNormalizationMode.Raw)
            else:
                self.Securities[asset["Ticker"]].SetDataNormalizationMode(DataNormalizationMode.TotalReturn)

        # Assumiamo che se possiamo effettuare un ordine per le azione, possiamo farlo anche per gli ETF.
        self.Schedule.On(self.DateRules.MonthStart(self.all_weather["Equity 1"]["Ticker"]),
                         self.TimeRules.AfterMarketOpen(self.all_weather["Equity 1"]["Ticker"]),
                         self.Rebalance)

    def OnData(self, data):
        '''OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.

        Arguments:
            data: Slice object keyed by symbol containing the stock data
        '''
        # Log di ogni dividendo ricevuto.
        # ---------------------------
        for kvp in data.Dividends:  # aggiornamento del dizionario dei dividendi
            div_ticker = kvp.Key
            div_distribution = kvp.Value.Distribution
            div_total_value = div_distribution * self.Portfolio[div_ticker].Quantity
            self.Log("DIVIDEND >> {0} - ${1} - ${2}".format(div_ticker, div_distribution, div_total_value))

    def Rebalance(self):
        month = self.Time.month

        # Esce se non vogliamo fare il ribilanciamento questo mese
        # Aggiungere altri mesi se vogliamo ribilanciare più spesso
        # ad es. per Marzo inserire 3 nella lista
        if month not in [1, 6]: return

        self.Log('-------------------->>')
        self.Log("{0} RE-BALANCE >> Total Value {1} | Cash {2}".format(
            self.Time.strftime('%B').upper(),
            self.Portfolio.TotalPortfolioValue,
            self.Portfolio.Cash))

        if self.savings_on and not self.first_rebalance:
            cash_after_savings = self.Portfolio.Cash + self.savings_amt
            self.Log("Top Up Savings >> New Cash Balance {0}".format(
                cash_after_savings))
            self.Portfolio.SetCash(cash_after_savings)

        # Ribilanciamento
        for key, asset in self.all_weather.items():
            holdings = self.Portfolio[asset["Ticker"]].Quantity
            price = self.Portfolio[asset["Ticker"]].Price

            self.Log("{0} >> Current Holdings {1} | Current Price {2}".format(
                self.Portfolio[asset["Ticker"]].Symbol,
                holdings,
                price))

            self.SetHoldings(asset["Ticker"], asset["Weight"])

        self.Log('-------------------->>')

        # Impostare il primo ribilanciamento a False così possiamo aggiungere il PAC dal prossimo
        self.first_rebalance = False