# modules in packages
import sys
from os import path
sys.path.append(path.dirname(path.dirname( path.abspath(__file__))))

class Logs(object):
    def __init__(self, filled_history, strategy_name):
        self.filled_history = filled_history
        self.strategy_name = strategy_name

    def __call__(self):
        csv_file_path = "csv_files/"
        csv_file_name = self.strategy_name + '.csv'
        self.file_name = csv_file_path + csv_file_name
        return self.file_name

    ''' record logs when you get position '''
    def entry_logs(self):
        entry_columns = ['orderID', 'timestamp', 'price', 'side', 'ordType']
        log_data = {}
        for column in entry_columns:
            variable_name = 'entry_' + column
            log_data[variable_name] = self.filled_history[1][column]
        return log_data

    ''' record logs when you get close '''
    def close_logs(self):
        close_columns = ['orderID', 'timestamp', 'price', 'ordType']
        log_data = {}
        for column in close_columns:
            variable_name = 'close_' + column
            log_data[variable_name] = self.filled_history[0][column]
        return log_data

    ''' only basic information about trading '''
    def basic_logs(self):
        entry_logs = self.entry_logs()
        close_logs = self.close_logs()
        entry_logs.update(close_logs)
        entry_logs['strategy_name'] = self.strategy_name
        return entry_logs

    '''
    report related:
    if the csv file name does not exist, make new csv file
    '''
    def new_csv_file(self):
        logs = self.basic_logs()
        init_columns = {}
        for column in logs.keys():
            init_columns[column] = []
        df = pd.DataFrame(init_columns)
        df.to_csv(self.file_name, mode="a", header=True, index=False)
        return

    '''
    report related:
    check wether content duplicated exists or not. if have same content,
    return True, if not return False
    '''
    def check_report_content_duplicated(self, report_data):
        df = pd.read_csv(self.file_name)
        past_entry_order_id = df["entry_orderID"].iloc[-1]
        recent_entry_order_id = report_data["entry_orderID"][0]
        past_close_order_id = df["close_orderID"].iloc[-1]
        recent_close_order_id = report_data["close_orderID"][0]

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
    def report(self, report_data):
        try:
            df = pd.DataFrame(report_data)
            df = self.change_korea_time(df)
            if self.check_report_content_duplicated(report_data):
                return
            else:
                df.to_csv(self.file_name, mode="a", header=False, index=False)

        # if file doest not exist, make new csv file
        except FileNotFoundError as e:
            self.new_csv_file()

        # if df is empty, the df is added first
        except IndexError as e:
            df.to_csv(self.file_name, mode="a", header=False, index=False)

        return
