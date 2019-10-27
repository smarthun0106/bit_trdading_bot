import pandas as pd

class Indicators(object):
    def __init__(self):
        pass

    '''
    moving_average:
    This is most simple indicator, but very useful and important one.
    you can put moving average length in lengths argument, the type of it must
    be the list, ex) [5, 10, 20]
    '''
    def moving_average(self, df, lengths):
        for length in lengths:
            column_name = 'ma' + str(length)
            df[column_name] = df['close'].rolling(window=length, center=False).mean()
            df[column_name] = round(df[column_name], 1)
        return df

    '''
    bollinger_bands:
    This indicator is 'bollinger bands', many investors love it.
    you can put another moving average length value and k value to change
    bollinger_bands high and bollinger_bands low
    '''
    def bollinger_bands(self, f_df, ma=20, k=2):
        f_name = 'ma' + str(ma)
        f_df[f_name] = f_df['close'].rolling(window=ma, center=False).mean()
        f_df['std20'] = f_df['close'].rolling(window=ma).std(ddof=0)
        f_df['bb_high'] = f_df[f_name] + f_df['std20']*k
        f_df['bb_low'] = f_df[f_name] - f_df['std20']*k
        f_df.dropna(inplace=True)
        return f_df

    def rsi(self):
        pass

    def macd(self):
        pass
