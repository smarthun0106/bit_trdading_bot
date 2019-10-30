# my modules
import bitapi.trading as bitmex
from strategy import strategies

# other modules
from pprint import pprint
import time

ma_strategy = strategies.MovingAverageStrategy01(
    symbol='XBT', interval='5m', lengths=[5],
    candle_count=5, short_pattern_value_k=0.8, long_pattern_value_k=0.2,
    time_delay=0.8, on_screen=True)
strategy_name = ma_strategy.__class__.__name__

trader = bitmex.Trading(
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
                trading_position = trading_strategy['ps'].iloc[0]

            if trading_position is 'l' or trading_position is 's':
                my_order = trader.trading(trading_strategy, strategy_name)
                switch = False
                if my_order is None :
                    switch = True

        except Exception as ex:
            print(ex)
