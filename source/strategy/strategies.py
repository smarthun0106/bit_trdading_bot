import sys
from os import path
sys.path.append(path.dirname(path.dirname( path.abspath(__file__))))

from bitapi.public_private import Public, Private
from .indicators import Indicators
import numpy as np
import time


'''
This stretagies includes moving average, bollinger_bands, rsi
'''
class MovingAverageStrategy(object):
    def __init__(self, symbol='XBT', interval='5m',
                 lengths=[5, 10, 25], candle_count=5,
                 short_pattern_value_k=0.8, long_pattern_value_k=0.2,
                 time_delay=1.0, on_screen=False):
        # arguments
        self.symbol = symbol
        self.interval = interval
        self.lengths = lengths
        self.candle_count = candle_count
        self.short_pattern_value_k = short_pattern_value_k
        self.long_pattern_value_k = long_pattern_value_k
        self.time_delay = time_delay
        self.on_screen = on_screen

        # moudle
        self.public = Public()

    ''' '''
    def import_data(self):
        time.sleep(self.time_delay)
        count = max(self.lengths) + self.candle_count
        df = self.public.candles(self.interval, self.symbol, count)
        return df

    ''' '''
    def df_moving_average(self):
        df = self.import_data()
        df = Indicators().moving_average(df, self.lengths)
        df.dropna(inplace=True)
        return df

    ''' '''
    def find_moving_average_names(self):
        df = self.df_moving_average()
        ma_columns = df.columns.str.contains('ma')
        self.ma_columns_names = df.loc[:, ma_columns].columns
        return df, self.ma_columns_names

    ''' '''
    def df_pattern_trend(self):
        df, ma_columns_names = self.find_moving_average_names()
        for ma_columns_name in ma_columns_names:
            pattern_name = 'pattern_' + ma_columns_name
            df[pattern_name] = np.where(df['close'] > df[ma_columns_name], 1, 0)
        return df

    ''' '''
    def df_pattern_trend_names(self):
        df = self.df_pattern_trend()
        ma_columns = df.columns.str.contains('pattern_')
        self.pattern_column_names = df.loc[:, ma_columns].columns
        return df, self.pattern_column_names

    ''' '''
    def shift_pattern_trend_data(self):
        df, pattern_column_names = self.df_pattern_trend_names()
        shift_count = self.candle_count + 1
        pattern_trend_names = []
        for pattern_column_name in pattern_column_names:
            for count in range(shift_count):
                names_shifted = pattern_column_name + '_' + str(count)
                df[names_shifted] = df[pattern_column_name].shift(count)
                pattern_trend_names.append(names_shifted)
        df.dropna(inplace=True)
        return df, pattern_trend_names

    ''' '''
    def pattern_score(self):
        df, pattern_trend_names = self.shift_pattern_trend_data()
        df['pattern_score'] = df[pattern_trend_names].sum(axis=1)
        return df

    ''' '''
    def calculate_pattern_value(self):
        num_candles = len(self.lengths) * self.candle_count
        short_pattern_value = int(num_candles * self.short_pattern_value_k)
        long_pattern_value = int(num_candles * self.long_pattern_value_k)
        return short_pattern_value, long_pattern_value, num_candles

    ''' '''
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

    ''' '''
    def present_candle_location_names(self):
        df = self.present_candle_location()
        location_columns = df.columns.str.contains('location')
        location_column_names = df.loc[:, location_columns].columns
        return df, location_column_names

    ''' '''
    def location_score(self):
        df, location_column_names = self.present_candle_location_names()
        df['location_score'] = df[location_column_names].sum(axis=1)
        return df

    ''' '''
    def print_on_screen(self, df, sp, lp, num_candles):
        output1 = "s_value: {0}/{1}, l_value: {2}/{3} --".format(
            sp, num_candles,
            lp, num_candles
        )
        output2 = "pattern_score: {0}, ps_score: {1}, ps: {2}, ".format(
            df['pattern_score'].iloc[0], df['location_score'].iloc[0],
            df['ps'].iloc[0], num_candles
        )
        output3 = 'pprice: {0}'.format(df['close'].iloc[0])
        print(output1, output2, output3)

    ''' '''
    def present_position(self):
        sp, lp, num_candles = self.calculate_pattern_value()
        df = self.location_score()
        short_boolen = (df['pattern_score'] > sp)
        long_boolen = (df['pattern_score'] < lp)
        df.loc[(df['location_score'] == 0) & sp, 'ps'] = 's'
        df.loc[(df['location_score'] == len(self.lengths)) & lp, 'ps'] = 'l'
        if self.on_screen:
            self.print_on_screen(df, sp, lp, num_candles)
        return df


#
# import sys
# from os import path
# sys.path.append(path.dirname(path.dirname( path.abspath(__file__))))
#
# from bitapi.public_private import Public, Private
# from .indicators import Indicators
# import numpy as np
# import time
#
#
#
#
# '''
# This stretagies includes moving average, bollinger_bands, rsi
# '''
# class MovingAverageStrategy(object):
#     def __init__(self, symbol='XBT', interval='5m',
#                  lengths=[5, 10, 25], candle_count=5,
#                  short_pattern_value_k=0.8, long_pattern_value_k=0.2,
#                  time_delay=1.0, on_screen=False):
#         # arguments
#         self.symbol = symbol
#         self.interval = interval
#         self.lengths = lengths
#         self.candle_count = candle_count
#         self.short_pattern_value_k = short_pattern_value_k
#         self.long_pattern_value_k = long_pattern_value_k
#         self.time_delay = time_delay
#         self.on_screen = on_screen
#
#         # moudle
#         self.public = Public()
#
#     ''' figure out wether the moving average is higher than close or not'''
#     def s_moving_average_preprocessing1(self):
#         time.sleep(self.time_delay)
#         df = self.public.candles(self.interval, self.symbol, max(self.lengths))
#         df = Indicators().moving_average(df, self.lengths)
#         ma_columns = df.columns.str.contains('ma')
#         self.ma_columns_names = df.loc[:, ma_columns].columns
#         return df
#
#     def s_moving_average_preprocessing2(self):
#         df = self.s_moving_average_preprocessing1()
#         self.names = []
#         for ma_columns_name in self.ma_columns_names:
#             pattern_name = 'pattern_' + ma_columns_name
#             df[pattern_name] = np.where(df['close'] > df[ma_columns_name], 1, 0)
#             for num in range(1, self.candle_count+1):
#                 name = pattern_name+'_'+str(num)
#                 df[name] = df[pattern_name].shift(num)
#                 self.names.append(name)
#         df['pattern_score'] = df[self.names].sum(axis=1)
#         return df.iloc[-1:]
#
#     # make short_pattern_value and long_pattern_value
#     def s_moving_average_preprocessing3(self):
#         df = self.s_moving_average_preprocessing2()
#         self.short_pattern_value = int(
#             len(self.names) * self.short_pattern_value_k)
#         self.long_pattern_value = int(
#             len(self.names) * self.long_pattern_value_k)
#         short_boolen = (df['pattern_score'] > self.short_pattern_value)
#         long_boolen = (df['pattern_score'] < self.long_pattern_value)
#         return df, short_boolen, long_boolen
#
#     # make moving_average_result
#     def s_moving_average_preprocessing4(self):
#             df, sb, lb = self.s_moving_average_preprocessing3()
#             names = []
#             for ma_columns_name in self.ma_columns_names:
#                 name = ma_columns_name+"_result"
#                 names.append(name)
#                 short_boolen = df[ma_columns_name] > df['close']
#                 df.loc[short_boolen, name] = 0
#                 long_boolen = df[ma_columns_name] < df['close']
#                 df.loc[long_boolen, name] = 1
#             df['ps_score'] = df[names].sum(axis=1)
#             return df, sb, lb
#
#     ''' This is a simple stretagy using moving average '''
#     def s_moving_average_position(self):
#         df, sb, lb = self.s_moving_average_preprocessing4()
#
#         # set in short or long
#         df.loc[(df['ps_score'] == 0) & sb, 'ps'] = 's'
#         df.loc[(df['ps_score'] == len(self.lengths)) & lb, 'ps'] = 'l'
#
#         # print on screen
#         if self.on_screen:
#             output1 = "s_value: {0}/{1}, l_value: {2}/{3} --".format(
#                 self.short_pattern_value, len(self.names),
#                 self.long_pattern_value, len(self.names)
#             )
#             output2 = "pattern_score: {0}, ps_score: {1}, ps: {2}, ".format(
#                 df['pattern_score'].iloc[0], df['ps_score'].iloc[0],
#                 df['ps'].iloc[0], len(self.names)
#             )
#             output3 = 'pprice: {0}'.format(df['close'].iloc[0])
#             print(output1, output2, output3)
#         return df
