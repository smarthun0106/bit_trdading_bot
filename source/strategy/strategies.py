import sys
from os import path
sys.path.append(path.dirname(path.dirname( path.abspath(__file__))))

from bitapi.basic_api import Public, Private
from .indicators import Indicators
import numpy as np
import time


'''
This stretagy is setted using an indicator of moving average.
'''
class MovingAverageStrategy01(object):
    def __init__(self, symbol='XBT', interval='5m',
                 lengths=[5, 10, 25], candle_count=5,
                 short_pattern_ratio=0.8, long_pattern_ratio=0.2,
                 time_delay=1.0, S_location_score=0, L_location_score=3,
                 S_gap=[2, -4], L_gap=[-2, 4],
                 on_screen=False):

        # arguments
        self.symbol = symbol ; self.interval = interval
        self.lengths = lengths ; self.candle_count = candle_count
        self.short_pattern_ratio = short_pattern_ratio
        self.long_pattern_ratio = long_pattern_ratio
        self.time_delay = time_delay
        self.S_location_score = S_location_score
        self.L_location_score = L_location_score
        self.S_gap = S_gap ; self.L_gap = L_gap
        self.on_screen = on_screen

        # moudle
        self.public = Public()

    ''' Get candle datas from bitmex public api '''
    def import_candles_data(self):
        time.sleep(self.time_delay)
        count = max(self.lengths) + self.candle_count
        df = self.public.candles(self.interval, self.symbol, count)
        return df

    ''' Add moving average '''
    def df_moving_average(self):
        df = self.import_candles_data()
        df = Indicators().moving_average(df, self.lengths)
        df.dropna(inplace=True)
        return df

    ''' find moving averages names '''
    def find_moving_average_names(self):
        df = self.df_moving_average()
        ma_columns = df.columns.str.contains('ma')
        self.ma_columns_names = df.loc[:, ma_columns].columns
        return df, self.ma_columns_names

    '''
    if past close price is higher than moving averages, the pattern trend
    is setted 1, it means its pattern is going high.
    if past close price is lower than moving averages, the pattern
    is setted 0, it means its pattern is going low
    '''
    def df_pattern_trend(self):
        df, ma_columns_names = self.find_moving_average_names()
        for ma_columns_name in ma_columns_names:
            pattern_name = 'pattern_' + ma_columns_name
            df[pattern_name] = np.where(df['close'] > df[ma_columns_name], 1, 0)
        return df

    ''' find pattern trend names to sum '''
    def df_pattern_trend_names(self):
        df = self.df_pattern_trend()
        ma_columns = df.columns.str.contains('pattern_')
        self.pattern_column_names = df.loc[:, ma_columns].columns
        return df, self.pattern_column_names

    ''' shift data to get past trend in one index '''
    def shift_pattern_trend_data(self):
        df, pattern_column_names = self.df_pattern_trend_names()
        shift_count = self.candle_count
        pattern_trend_names = []
        for pattern_column_name in pattern_column_names:
            for count in range(shift_count):
                names_shifted = pattern_column_name + '_' + str(count)
                df[names_shifted] = df[pattern_column_name].shift(count)
                pattern_trend_names.append(names_shifted)
        df.dropna(inplace=True)
        return df, pattern_trend_names

    '''
    sum in past pattern trend for pattern scored,
    it is added to dataframe
    '''
    def pattern_score(self):
        df, pattern_trend_names = self.shift_pattern_trend_data()
        df['pattern_score'] = df[pattern_trend_names].sum(axis=1)
        return df

    '''
    make condition to decide wether short or long with
    ratio of pattern score
    '''
    def calculate_pattern_value(self):
        num_candles = len(self.lengths) * self.candle_count
        short_pattern_value = int(num_candles * self.short_pattern_ratio)
        long_pattern_value = int(num_candles * self.long_pattern_ratio)
        return short_pattern_value, long_pattern_value, num_candles

    ''' determin the status present price location '''
    def present_candle_location(self):
        df = self.pattern_score()
        ma_columns_names = self.ma_columns_names
        for ma_columns_name in ma_columns_names:
            name = ma_columns_name+"_location"
            short_boolen = df[ma_columns_name] > df['close']
            long_boolen = df[ma_columns_name] < df['close']
            df.loc[short_boolen, name] = 0
            df.loc[long_boolen, name] = 1
        return df

    ''' find location names '''
    def present_candle_location_names(self):
        df = self.present_candle_location()
        location_columns = df.columns.str.contains('location')
        location_column_names = df.loc[:, location_columns].columns
        return df, location_column_names

    ''' get location score '''
    def location_score(self):
        df, location_column_names = self.present_candle_location_names()
        df['location_score'] = df[location_column_names].sum(axis=1)
        return df

    ''' get the gap between present price and moving averages '''
    def present_gap(self):
        df = self.location_score().iloc[1:2]
        df['gap'] = df['close'] - df[self.ma_columns_names[0]]
        return df

    ''' output text to monitor '''
    def print_on_screen(self, df, sp, lp, num_candles):
        output1 = "S_ratio: {0}/{1}, L_ratio: {2}/{3} --".format(
            sp, num_candles,
            lp, num_candles
        )
        output2 = "pattern_score: {0}, ps_score: {1}, gap: {2},".format(
            df['pattern_score'].iloc[0], df['location_score'].iloc[0],
            int(df['gap'].iloc[0]), num_candles
        )
        output3 = 'ps: {0},'.format(df['ps'].iloc[0])
        output4 = 'pp: {0}'.format(df['close'].iloc[0])
        print(output1, output2, output3, output4)

    ''' set which condition is short or long '''
    def present_position(self):
        sp, lp, num_candles = self.calculate_pattern_value()
        df = self.present_gap()

        S1 = (df['location_score'] == self.S_location_score)
        L1 = (df['location_score'] == self.L_location_score)

        S2 = (df['pattern_score'] > sp)
        L2 = (df['pattern_score'] < lp)

        S3 = (df['gap'] < self.S_gap[0]) & (df['gap'] > self.S_gap[1])
        L3 = (df['gap'] > self.L_gap[0]) & (df['gap'] < self.L_gap[1])

        df.loc[S1 & S2 & S3, 'ps'] = 's'
        df.loc[L1 & L2 & L3, 'ps'] = 'l'

        if self.on_screen:
            self.print_on_screen(df, sp, lp, num_candles)
        return df
