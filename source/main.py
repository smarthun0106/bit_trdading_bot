# my modules
import bitapi.trading as bitmex
from strategy import strategies

# other modules
from pprint import pprint
import time

ma_strategy = strategies.MovingAverageStrategy(
    symbol='XBT', interval='5m', lengths=[5],
    candle_count=5, short_pattern_value_k=0.8, long_pattern_value_k=0.2,
    time_delay=0.8, on_screen=True)

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
                present_position = trading_strategy['ps'].iloc[0]

            if present_position is 'l' or present_position is 's':
                my_order = trader.trading(
                        trading_strategy, 'moving_average_position')
                switch = False
                if my_order is None :
                    switch = True

        except Exception as ex:
            print(ex)
