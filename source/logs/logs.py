# modules in packages
import sys
from os import path
sys.path.append(path.dirname(path.dirname( path.abspath(__file__))))

import pandas as pd
import numpy as np

class Logs(object):
    def __init__(self, filled_history, strategy_name):
        self.filled_history = filled_history
        self.strategy_name = strategy_name


        csv_file_path = "logs/csv_files/"
        csv_file_name = self.strategy_name + '.csv'
        self.file_name = csv_file_path + csv_file_name

    def __call__(self):
        pass

    ''' record logs when you get position '''
    def entry_logs(self):
        entry_columns = ['orderID', 'timestamp', 'price', 'side', 'ordType']
        log_data = {}
        for column in entry_columns:
            variable_name = 'entry_' + column
            log_data[variable_name] = [self.filled_history[1][column]]
        return log_data

    ''' record logs when you get close '''
    def close_logs(self):
        close_columns = ['orderID', 'timestamp', 'price', 'ordType']
        log_data = {}
        for column in close_columns:
            variable_name = 'close_' + column
            log_data[variable_name] = [self.filled_history[0][column]]
        return log_data

    ''' only basic information about trading '''
    def basic_logs(self):
        e_logs = self.entry_logs()
        c_logs = self.close_logs()

        e_logs.update(c_logs)
        e_logs['strategy_name'] = self.strategy_name
        self.logs = e_logs
        return self.logs

    '''
    report related:
    if the csv file name does not exist, make new csv file
    '''
    def new_csv_file(self):
        init_columns = {}
        for column in self.logs.keys():
            init_columns[column] = []
        df = pd.DataFrame(init_columns)
        df.to_csv(self.file_name, mode="a", header=True, index=False)
        print(df)
        return

    '''
    report related:
    check wether content duplicated exists or not. if have same content,
    return True, if not return False
    '''
    def check_report_content_duplicated(self):
        df = pd.read_csv(self.file_name)
        past_entry_order_id = df["entry_orderID"].iloc[-1]
        recent_entry_order_id = self.logs["entry_orderID"][0]
        past_close_order_id = df["close_orderID"].iloc[-1]
        recent_close_order_id = self.logs["close_orderID"][0]

        if past_entry_order_id == recent_entry_order_id: return True
        if past_close_order_id == recent_close_order_id: return True
        return False

    ''' report related: convert timestamp to KST(Korea Standard Time) '''
    def change_korea_time(self, df):
        nine_hours = pd.Timedelta('9 hours')
        df['entry_timestamp'] = pd.to_datetime(df['entry_timestamp'])+nine_hours
        df['close_timestamp'] = pd.to_datetime(df['close_timestamp'])+nine_hours
        return df

    ''' report related: save report as csv file '''
    def report(self):
        try:
            self.basic_logs()
            df = pd.read_csv(self.file_name)
            df = pd.DataFrame(self.logs)
            df = self.change_korea_time(df)
            if self.check_report_content_duplicated():
                return
            else:
                df.to_csv(self.file_name, mode="a", header=False, index=False)
            print('index added')

        # if file doest not exist, make new csv file
        except FileNotFoundError as e:
            self.new_csv_file()
            print('new csv file added at '.format(self.file_name))

        # if df is empty, the df is added first
        except IndexError as e:
            df.to_csv(self.file_name, mode="a", header=False, index=False)
            print('first index added')

        return
