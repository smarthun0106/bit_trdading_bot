import sys
from os import path
sys.path.append(path.dirname(path.dirname( path.abspath(__file__))))

from bitapi.basic_api import Public, Private
from strategy.indicators import Indicators
import numpy as np
import time

'''
This stretagy is setted using an indicator of moving average.
'''
class MovingAverageStrategy01(object):
    def __init__(self, symbol='XBT', interval='5m',
                 lengths=[5, 10, 25], control=['high', 'high', 'low'],
                 candle_count=5, short_pattern_ratio=0.8, long_pattern_ratio=0.2,
                 time_delay=1.0, S_location_score=0, L_location_score=3,
                 S_gap=[2, -4], L_gap=[-2, 4], on_screen=False):

        # arguments
        self.symbol = symbol
        self.interval = interval
        self.lengths = lengths
        self.control = control
        self.candle_count = candle_count
        self.short_pattern_ratio = short_pattern_ratio
        self.long_pattern_ratio = long_pattern_ratio
        self.time_delay = time_delay
        self.S_location_score = S_location_score
        self.L_location_score = L_location_score
        self.S_gap = S_gap
        self.L_gap = L_gap
        self.on_screen = on_screen

        # moudle
        self.public = Public()

    def find_column_names(self, df, text):
        name_contained = df.columns.str.contains(text)
        columns = df.loc[:, name_contained].columns
        return columns

    ''' Get candle datas from bitmex public api '''
    def bring_candles_data(self):
        time.sleep(self.time_delay)
        count = max(self.lengths) + self.candle_count
        df = self.public.candles(self.interval, self.symbol, count)
        return df

    ''' Add moving average '''
    def adding_moving_average(self, df):
        df = Indicators().moving_average(df, self.lengths)
        df.dropna(inplace=True)
        return df

    '''
    This function is for adding upward_ features
    moving average that is higher than close will be filled with int 1
    Dataframe will be get features words start with upward_
    ex) upward_ma5, upward_ma10....
    '''
    def ma_higher_than_close(self, df, ma_name):
        column_name = 'pattern_' + ma_name
        df.loc[df['close'] > df[ma_name], column_name] = 1
        return df

    '''
    This function is for adding downward_ features
    moving average that is lower than close will be filled with int 1
    Dataframe will be get features words start with downward_
    ex) downward_ma5, downward_ma10....
    '''
    def ma_lower_than_close(self,  df, ma_name):
        column_name = 'pattern_' + ma_name
        df.loc[df['close'] < df[ma_name], column_name] = 1
        return df

    def adding_pattern(self, df):
        ma_names = self.find_column_names(df, 'ma')
        for o, c in enumerate(self.control):
            if c is 'high':
                df = self.ma_higher_than_close(df, ma_names[o])
            elif c is 'low':
                df = self.ma_lower_than_close(df, ma_names[o])
        df.fillna(0, inplace=True)
        return df

    def adding_historical_pattern(self, df):
        pattern_ma_names = self.find_column_names(df, 'pattern')
        for pattern_ma_name in pattern_ma_names:
            for i in range(self.candle_count):
                column_name = pattern_ma_name + '_' + str(i+1)
                df[column_name] = df[pattern_ma_name].shift(i+1)
        df.dropna(inplace=True)
        return df

    def adding_pattern_score(self, df):
        ma_names = self.find_column_names(df, 'pattern')


    def bullish_pattern(self):
        pass

    def bearish_pattern(self):
        pass

    def strategy_dataframe(self):
        df = self.bring_candles_data()
        df = self.adding_moving_average(df)
        df = self.adding_pattern(df)
        df = self.adding_historical_pattern(df)
        return df



first_strategy = MovingAverageStrategy01(symbol='XBT', interval='5m',
             lengths=[5, 10], control=['high', 'low'], candle_count=1,
             short_pattern_ratio=0.8, long_pattern_ratio=0.2,
             time_delay=1.0, S_location_score=0, L_location_score=3,
             S_gap=[2, -4], L_gap=[-2, 4], on_screen=False)
print(first_strategy.strategy_dataframe())
