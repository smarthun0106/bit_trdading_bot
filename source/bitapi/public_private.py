import sys
from os import path
sys.path.append(path.dirname(path.dirname( path.abspath(__file__))))
from utility.utility import Utils
from settings import BITMEX_API_KEY, BITMEX_SECRET_KEY

import time
import requests
import json
import pandas as pd

from ccxt import bitmex

'''
This app's purpose is made for real trading and real test.
So These datas return only essential datas.

These app is useful for :
- who wants to get the clean raw data(candles),
you can get 1m, 5m, 1h, 1d datas but the limit is 1000 rows
- who wants to get only simple datas

you can use Public API like getting datas(candles) without making "settings.py".
but you have to make "settings.py" file to execute Private API for security

* I hope my codes will be helpful for you

'''

# Public API
class Public(object):
    def __init__(self):
        self.url = "https://www.bitmex.com"

    # korea time converter
    def convert_kst(self, interval, json_data, option=None):
        if option == 'original' : return pd.DataFrame(json_data)
        if interval == '1m':
            time_controller = None
        if interval == "5m":
            time_controller = '8hours 55minutes'
        if interval == "1h":
            time_controller = None
        if interval == "1d":
            time_controller = None

        f_df = pd.DataFrame(json_data)
        time_delta = pd.Timedelta(time_controller)
        f_df['timestamp'] = pd.to_datetime(f_df['timestamp']) + time_delta
        f_df = f_df[['timestamp', 'open', 'high', 'low','close', 'volume']]
        f_df = f_df.sort_values(by='timestamp')
        return f_df

    '''
    interval : '1m', '5m', '1h', '1d'
    currency : 'XBT'
    count : maximum data you can get is 1000
    option : 'original', you will get orginal data
    '''
    # get candles ex) candles('5m', 'XBT', 20)
    def candles(self, interval, symbol, count, option=None):
        path = "/api/v1/trade/bucketed"
        # connect to the public API
        parameters = {
            "binSize": interval,
            "count": count, "reverse": 'true',
            "partial": 'true', "symbol": symbol,
        }
        response = requests.get(self.url + path, params=parameters)
        f_df = self.convert_kst(interval, response.json(), option)
        return f_df

    # ex current_order_book(XBT)
    def current_order_book(self, symbol, depth=25):
        path = "/api/v1/orderBook/L2"
        parameters = { "symbol": symbol, "depth": depth }
        response = requests.get(self.url + path, params=parameters)
        sell_side = response.json()[24]['price']
        buy_side = response.json()[25]['price']
        return sell_side, buy_side

# Private API
class Private(object):
    def __init__(self):
        api_key = BITMEX_API_KEY
        api_secret = BITMEX_SECRET_KEY
        self.bit = bitmex({ 'apiKey': api_key, 'secret': api_secret})

    ''' make order '''
    def create_order(self, symbol, type, side, amount, price=None):
        if symbol=='XBT' : symbol = 'BTC/USD'
        if type == "Limit":
            result = self.bit.create_order(symbol, type, side, amount, price)
        elif type == "Market" :
            result = self.bit.create_order(symbol, type, side, amount)
        return result

    ''' check id to cancel the order '''
    def cancel_order(self, symbol, id):
        if symbol=='XBT' : symbol = 'BTC/USD'
        self.bit.cancel_order(id)

    ''' you can check your order status, no order return None '''
    def order_status(self, symbol, row=0):
        if symbol=='XBT' : symbol = 'BTC/USD'
        result = self.bit.fetchOpenOrders(symbol)
        if len(result) == 0: return None

        if result[row]['side'] == "sell" : side = "s"
        if result[row]['side'] == "buy" : side = "l"
        price = result[row]['price'] ; amount = result[row]['amount']
        id = result[row]['id']
        result = {
            "position" : side, "price" : price,
            "amount" : amount, "id" : id
        }
        return result

    ''' you can check your position status, no position return None '''
    def position_status(self, symbol, row=0):
        if symbol=='XBT' : symbol = 'BTC/USD'
        result = self.bit.private_get_position(symbol)
        if result[row]['avgEntryPrice'] == None : return None

        price = result[row]['avgEntryPrice']
        amount = result[row]['currentQty']
        commission = result[row]['commission']
        leverage = result[row]['leverage']
        result = {
            "price" : price, "amount" : amount,
            "commission" : commission, "leverage" : leverage
        }
        return result

    ''' close your position '''
    def position_close(self, symbol, type, price=0):
        if symbol=='XBT' : symbol = 'XBTUSD'
        if price == 0:
            order_close = { "symbol": symbol, "type": type}
        else:
            order_close = {
                "symbol": symbol, "type": type,
                "price": price
            }
        self.bit.private_post_order_closeposition(order_close)

    ''' return only filled history '''
    def filled_history(self):
        filled_history = self.bit.privateGetExecutionTradeHistory(
            {'reverse' : True}
        )
        return filled_history


class SmartPublicPrivate(object):
    '''
    init:

    '''
    def __init__(self, symbol='XBT', amount=1,
                 order_type='Limit', stop_type='Market',
                 target_unit_price=20, stop_loss_unit_price=20,
                 time_delay=0.5):
        # arguments
        self.symbol = symbol
        self.amount = amount
        self.order_type = order_type
        self.stop_type = stop_type
        self.target_unit_price = target_unit_price
        self.stop_loss_unit_price = stop_loss_unit_price
        self.time_delay = time_delay

        # import current file class
        self.utils = Utils()
        self.public = Public()
        self.private = Private()



    def import_datas(self):
        self.order_book_sell_price, self.order_book_buy_price = \
                            self.public.current_order_book(self.symbol)
        time.sleep(self.time_delay)

        self.my_position = self.private.position_status(self.symbol)
        time.sleep(self.time_delay)

        self.my_order = self.private.order_status(self.symbol)
        return

    '''
    buy_sell:

    '''
    def buy_sell(self, position):
        if position is 's':
            self.private.create_order(
                        self.symbol, self.order_type, 'sell',
                        self.amount, self.order_book_sell_price)

        if position is 'l':
            self.private.create_order(
                        self.symbol, self.order_type, 'buy',
                        self.amount, self.order_book_buy_price)

        time.sleep(self.time_delay)
        return

    '''
    stop_cancel_close:

    '''
    def stop_cancel_close(self):
        self.private.cancel_order(self.symbol, self.my_order['id'])
        time.sleep(self.time_delay)
        if self.stop_type is 'Market':
            self.private.position_close(self.symbol, 'Market')
        if self.stop_type is 'Limit':
            self.private.position_close(self.symbol, 'Limit', price=0)
        return

    '''
    stop_loss:

    '''
    def stop_loss(self):
        if self.my_position['amount'] > 0:
            stop_price = self.my_position['price'] - self.stop_loss_unit_price
            if stop_price >= self.order_book_sell_price:
                self.stop_cancel_close()

        if self.my_position['amount'] < 0:
            stop_price = self.my_position['price'] + self.stop_loss_unit_price
            if stop_price <= self.order_book_buy_price:
                self.stop_cancel_close()
        return

    '''
    ordering:
    If an order price you submitted is higher or lower than orderbook,
    it is canceled
    '''
    def ordering(self):
        if self.my_order["position"] is "s":
            if self.my_order['price'] != self.order_book_sell_price:
                self.private.cancel_order(self.symbol, self.my_order['id'])

        elif self.my_order["position"] is "l":
            if self.my_order['price'] != self.order_book_buy_price:
                self.private.cancel_order(self.symbol, self.my_order['id'])
        return

    '''
    close_price:

    '''
    def close_price(self):
        if self.my_position['amount'] < 0:
            price = int(self.my_position['price'] - self.target_unit_price)
            position = 'S'

        elif self.my_position['amount'] > 0:
            price = int(self.my_position['price'] + self.target_unit_price)
            position = 'L'
        self.private.position_close(self.symbol, self.order_type, price)
        return

    '''
    report_data:


    '''
    def report_data(self):
        time.sleep(self.time_delay)
        filled_history = self.private.filled_history()
        strategy_name = self.strategy_name
        # entry order, make order name insted of order id
        entry_order_id = filled_history[1]["orderID"]
        entry_date = filled_history[1]["timestamp"]
        entry_price = filled_history[1]["price"]
        entry_side = filled_history[1]["side"]
        entry_order_type = filled_history[1]["ordType"]

        # close order
        close_order_id = filled_history[0]["orderID"]
        close_date = filled_history[0]["timestamp"]
        close_price = filled_history[0]["price"]
        close_order_type = filled_history[0]["ordType"]

        # make dic type data
        report_data = {
            "strategy_name" : [strategy_name],
            "entry_order_id" : [entry_order_id], "entry_date" : [entry_date],
            "entry_price" : [entry_price], "entry_side" : [entry_side],
            "entry_order_type" : [entry_order_type],
            "close_order_id" : [close_order_id],  "close_date" : [close_date],
            "close_price" : [close_price],
            "close_order_type" : [close_order_type]
        }
        return report_data

    '''
    trading:

    '''
    def trading(self, trading_strategy, strategy_name):
        self.import_datas()
        trading_strategy.name = strategy_name
        self.strategy_name = trading_strategy.name
        position = trading_strategy['ps'].iloc[0]

        if self.my_order is None and self.my_position is None:
            self.buy_sell(position)
            self.utils.report(self.report_data())

        if self.my_order is not None and self.my_position is not None:
            self.stop_loss()

        if self.my_order is not None:
            if self.my_position is None:
                self.ordering()

        if self.my_order is None:
            if self.my_position is not None:
                self.close_price()
        return self.my_order, self.my_position
