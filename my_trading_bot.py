import numpy as np 
import yfinance as yf
from datetime import datetime
import time

class TradingStrategy:
    def __init__(self, name):
        self.__name = name

    def generate_signal(self, price_data):
        print("This method should be overridden by subclasses")
        return "hold"
    
    @property
    def name(self):
        return self.__name


# moving average strategy 
class SMAStrategy(TradingStrategy):
    def __init__(self,short_window=3, long_window=5):
        super().__init__("Simple Moving Average Strategy")
        self.__short_window = short_window
        self.__long_window = long_window

    def generate_signal(self, price_data):
        if len(price_data) < self.__long_window:
            return "hold"
        
        short_avg = sum(price_data[-self.__short_window:]) / self.__short_window
        long_avg = sum(price_data[-self.__long_window:]) / self.__long_window
        
        if short_avg > long_avg:
            return "buy"
        elif short_avg < long_avg:
            return "sell"
        else:
            return "hold"

    @property
    def short_window(self):
        return self.__short_window

    @property
    def long_window(self):
        return self.__long_window



class Trade:
    def __init__(self, strategy_name, signal, amount):
        self.__strategy_name = strategy_name
        self.__signal = signal
        self.__amount = amount
        self.__timestamp = datetime.now()

    def execute(self):
        print(f"Executing {self.__signal} for {self.__amount} units using {self.__strategy_name} at {self.__timestamp}")

    @property
    def strategy_name(self):
        return self.__strategy_name

    @property
    def signal(self):
        return self.__signal

    @property
    def amount(self):
        return self.__amount

    @property
    def timestamp(self):
        return self.__timestamp



# mock trading  :


class MockTradingAPI:
    def __init__(self, balance):
        self.__balance = balance

    def place_order(self, trade, price):
        if trade.signal == "buy" and self.__balance >= trade.amount * price:
            self.__balance -= trade.amount * price
            print(f"Placed buy order for {trade.amount} units at {price}. Remaining balance: {self.__balance}")
        elif trade.signal == "sell":
            self.__balance += trade.amount * price
            print(f"Placed sell order for {trade.amount} units at {price}. Remaining balance: {self.__balance}")
        else:
            print("Insufficient balance or invalid signal.")

    def get_balance(self):
        return self.__balance

        

class TradingSystem:
    def __init__(self, api, strategy, symbol):
        self.__api = api
        self.__strategy = strategy
        self.__symbol = symbol
        self.__price_data = []

    def fetch_price_data(self):
        data = yf.download(tickers=self.__symbol, period='1d', interval='1m')
        if not data.empty:
            price = data['Close'].iloc[-1]
            self.__price_data.append(price)
            if len(self.__price_data) > self.__strategy.long_window:
                self.__price_data.pop(0)
            print(f"Fetched new price data: {price}")
        else:
            print("No data fetched")

    def run(self):
        self.fetch_price_data()
        signal = self.__strategy.generate_signal(self.__price_data)
        print(f"Generated signal: {signal}")
        if signal in ["buy", "sell"]:
            trade = Trade(self.__strategy.name, signal, 1)
            trade.execute()
            self.__api.place_order(trade, self.__price_data[-1])

    @property
    def api(self):
        return self.__api

    @property
    def strategy(self):
        return self.__strategy

    @property
    def symbol(self):
        return self.__symbol

    @property
    def price_data(self):
        return self.__price_data





if __name__ == "__main__":
    
    symbol = 'AAPL'

    api = MockTradingAPI(balance=10000)
    strategy = SMAStrategy()
    system = TradingSystem(api, strategy, symbol)

    for _ in range(10):
        system.run()
        print(f"Remaining balance: {api.get_balance()}")
        time.sleep(60)