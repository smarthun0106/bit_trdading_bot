# my modules
import bitapi.trading as bitmex
from strategy import strategies
from utility import utility

# other modules
from pprint import pprint
import time

ma_strategy = strategies.MovingAverageStrategy01(
    symbol='XBT', interval='5m', lengths=[8, 20, 35],
    candle_count=8, short_pattern_value_k=0.8, long_pattern_value_k=0.2,
    time_delay=0.5, on_screen=True)
strategy_name = ma_strategy.__class__.__name__

trader = bitmex.Trading(
    symbol='XBT', amount=1, order_type='Limit',
    stop_type='Market',
    target_unit_price=45, stop_loss_unit_price=30,
    time_delay=0.7)


switch = True
if __name__ == '__main__':
    while True:
        try:
            # strategy setting
            if switch:
                trading_strategy = ma_strategy.present_position()
                position = trading_strategy['ps'].iloc[0]
            if position is 'l' or position is 's':
                my_order = trader.trading(position, strategy_name)
                switch = False
                if my_order is None:
                    switch = True

        except Exception as ex:
            utility.Utils().alerts(ex, 'error')
            print(ex)
