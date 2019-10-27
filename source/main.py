# my modules
import bitapi.public_private as bitmex
from strategy import strategies
from math import isnan

# other modules
from pprint import pprint
import time

ma_strategy = strategies.MovingAverageStrategy(
    symbol='XBT', interval='5m', lengths=[5, 10, 25],
    candle_count=8, short_pattern_value_k=0.8, long_pattern_value_k=0.2,
    time_delay=0.8, on_screen=True)

trader = bitmex.SmartPublicPrivate(
    symbol='XBT', amount=1, order_type='Limit',
    stop_type='Market',
    target_unit_price=20, stop_loss_unit_price=20,
    time_delay=0.5)

switch = True
if __name__ == '__main__':
    while True:
        try:
            # strategy setting
            if switch:
                trading_strategy = ma_strategy.present_position()
                present_position = trading_strategy['ps'].iloc[0]
        except Exception as ex:
            print(ex)
        else:
            if present_position is 'l' or present_position is 's':
                my_order, my_position = trader.trading(
                        trading_strategy, 'moving_average_position')
                switch = False
                if my_order is None and my_position is None:
                    switch = True
