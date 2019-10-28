# modules in packages
if __name__ == '__main__':
    from basic_api import Public, Private
else:
    from .basic_api import Public, Private
from utility.utility import Utils
from reports.logs import Logs

# python moudles
import time

class Trading(object):
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
        self.public = Public()
        self.private = Private()
        self.utils = Utils()

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
    stop_loss_cancel_loss:

    '''
    def stop_loss_cancel_loss(self):
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
                self.stop_loss_cancel_loss()

        if self.my_position['amount'] < 0:
            stop_price = self.my_position['price'] + self.stop_loss_unit_price
            if stop_price <= self.order_book_buy_price:
                self.stop_loss_cancel_loss()
        return

    '''
    ordering:
    If an order price you submitted is higher or lower than orderbook,
    it is canceled.
    It chase the order book till the strategy output position.
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
    def report_data(self, filled_history):
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

        # get bot_signal that is trading from bot
        bot_text = 'Submitted via API.'
        history_text_01 = filled_history[1]['text']
        history_text_00 = filled_history[0]['text']

        if bot_text is history_text_01:
            if bot_text is history_text_00:
                bot_trading = True
        else:
            bot_trading = False
        return report_data, bot_trading

    def import_api_data(self):
        self.my_position = self.private.position_status(self.symbol)
        time.sleep(self.time_delay)
        self.my_order = self.private.order_status(self.symbol)
        time.sleep(self.time_delay)
        self.order_book_sell_price, self.order_book_buy_price = \
                            self.public.current_order_book(self.symbol)
        return

    '''
    trading:

    '''
    def trading(self, trading_strategy, strategy_name):]
        self.import_api_data()

        trading_strategy.name = strategy_name
        self.strategy_name = trading_strategy.name

        if self.my_order is None and self.my_position is None:
            position = trading_strategy['ps'].iloc[0]
            self.buy_sell(position)

            filled_history = self.private.filled_history()
            time.sleep(self.time_delay)
            report_data, bot_trading = self.report_data(filled_history)
            if bot_trading:
                self.utils.report(report_data)

        elif self.my_order is not None and self.my_position is not None:
            self.stop_loss()

        elif self.my_order is not None:
            if self.my_position is None:
                self.ordering()

        elif self.my_order is None:
            if self.my_position is not None:
                self.close_price()

        self.my_order = self.private.order_status(self.symbol)
        return self.my_order
