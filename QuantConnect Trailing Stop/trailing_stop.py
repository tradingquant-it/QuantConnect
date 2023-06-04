class ParticleResistanceCircuit(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2018, 11, 20)  # Data Inizio
        self.SetCash(100000)  # Capitale Iniziale
        self.symbol = "SPY"
        self.AddEquity(self.symbol, Resolution.Minute)

        # distanza del trailing in $
        self.trail_dist = 10

        # dichiara un attributo che useremo per memorizzare il nostro stop loss ticket.
        self.sl_order = None

        # Dichiara un attributo che useremo per memorizzare l'ultimo livello
        # di trailing stop usato. Lo useremo per decidere se spostare lo stop
        self.last_trail_level = None

    def OnOrderEvent(self, OrderEvent):
        '''Event when the order is filled. Debug log the order fill. :OrderEvent:'''

        if OrderEvent.FillQuantity == 0:
            return

        # otteniamo l'ordine eseguito
        Order = self.Transactions.GetOrderById(OrderEvent.OrderId)

        # Log dei dettagli dell'ordine eseguito
        self.Log("ORDER NOTIFICATION >> {} >> Status: {} Symbol: {}. Quantity: "
                 "{}. Direction: {}. Fill Price {}".format(str(Order.Tag),
                                                           str(OrderEvent.Status),
                                                           str(OrderEvent.Symbol),
                                                           str(OrderEvent.FillQuantity),
                                                           str(OrderEvent.Direction),
                                                           str(OrderEvent.FillPrice)))

    def OnData(self, data):
        '''OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
            Arguments:
                data: Slice object keyed by symbol containing the stock data
        '''

        # Dobbiamo verificare che il simbolo contengai  dati prima di provare ad
        # accedere a OHLC. In caso contrario, viene sollevata un'eccezione se i dati sono mancanti.
        if data.ContainsKey(self.symbol) and data.HasData:

            # Alias
            # ------------------------------------------
            holdings = self.Portfolio[self.symbol].Quantity
            value = self.Portfolio.TotalPortfolioValue
            cash = self.Portfolio.Cash

            # Eccezione se non ci sono i dati
            try:
                O = round(data[self.symbol].Open, 2)
                H = round(data[self.symbol].High, 2)
                L = round(data[self.symbol].Low, 2)
                C = round(data[self.symbol].Close, 2)
            except AttributeError:
                self.Log('>> {} >> Missing Data')
                return

            # Calcola il nostro livello SL di base. Viene utilizzato per l'inserimento iniziale.
            # Lo useremo anche per il confronto con il livello del trailing precedente.
            base_sl_level = round(C - self.trail_dist, 2)

            # Log OHLC - Questo può essere utile per il debug per vedere dove si sta muovendo il prezzo
            self.Log('>> {}      >> ON DATA >> >> >> >> >> >>'.format(self.symbol))
            self.Log('>> OHLC     >> O:{} H:{} L:{} C:{}'.format(O, H, L, C))
            self.Log('>> SL       >> Base Level:{} Last Trail Level:{}'.format(base_sl_level, self.last_trail_level))
            self.Log('>> Account  >> Cash:{}, Val:{}, Holdings:{}'.format(cash, value, holdings))

            if not self.Portfolio.Invested:
                self.MarketOrder(self.symbol, 10, False, 'Long Entry')
                self.sl_order = self.StopMarketOrder(self.symbol, -10, base_sl_level, 'SL')
                self.last_trail_level = base_sl_level

            else:
                if base_sl_level > self.last_trail_level:
                    self.Log('>> Updating Trailing Stop >>')

                    # Aggiornamento ordine stoploss
                    update_order_fields = UpdateOrderFields()
                    update_order_fields.StopPrice = base_sl_level
                    self.sl_order.Update(update_order_fields)

                    # Log dell'ultimo sl_level
                    self.last_trail_level = base_sl_level