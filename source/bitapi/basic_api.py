from settings import BITMEX_API_KEY, BITMEX_SECRET_KEY
import time
import requests
import json
import pandas as pd
from ccxt import bitmex

''' This Public is made by pour bitmex api '''
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
        f_df = f_df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
        f_df = f_df.sort_values(by='timestamp')
        return f_df

    '''
    interval : '1m', '5m', '1h', '1d'
    currency : 'XBT'
    count : maximum data you can get is 1000
    option : 'original', you will get orginal data
    using example : df = candles('5m', 'XBT', 20)
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
        df = self.convert_kst(interval, response.json(), option)
        return df

    # ex current_order_book(XBT)
    def current_order_book(self, symbol, depth=25):
        path = "/api/v1/orderBook/L2"
        parameters = { "symbol": symbol, "depth": depth }
        response = requests.get(self.url + path, params=parameters)
        sell_side = response.json()[24]['price']
        buy_side = response.json()[25]['price']
        return sell_side, buy_side

''' This private api is not made by bitmex api, used ccxt pacakges '''
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
