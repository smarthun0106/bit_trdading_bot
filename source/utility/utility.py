import sys
from os import path
sys.path.append(path.dirname(path.dirname( path.abspath(__file__))))
from settings import TELEGRAM_ERROR_BOT_TOKEN, TELEGRAM_REPORT_BOT_TOKEN

from datetime import datetime
import pandas as pd

class Utils(object):
    ''' make standard time clearer '''
    def time_now(self):
        dt = datetime.now()
        time_now = dt.strftime('%Y-%m-%d %H:%M:%S.%f')
        return time_now[:-7]

    ''' telegram related: get url path included token '''
    def telegram_sender(self, token):
        url = "https://api.telegram.org"
        path = "/bot{0}/sendMessage".format(token)
        url_path = url + path
        return url_path

    ''' telegram related: make variety of alerts '''
    def alerts(self, text, type):
        if type is 'error':
            token = TELEGRAM_ERROR_BOT_TOKEN
        elif type is 'report':
            token = TELEGRAM_REPORT_BOT_TOKEN

        url_path = self.telegram_sender(token)
        parameters = { "chat_id" : "756052880", "text" : text }
        r = requests.get(url_path, params=parameters)
        return r

    ''' report related: make csv file name '''
    def csv_file_name(self):
        csv_file_path = ""
        csv_file_name = "strategy_result.csv"
        self.file_name = csv_file_path + csv_file_name
        return

    '''
    report related:
    if the csv file name does not exist, make new csv file
    '''
    def new_csv_file(self):
        report_data = {
            "strategy_name" : [], "entry_order_id" : [],
            "entry_date" : [], "entry_price" : [],
            "entry_side" : [], "entry_order_type" : [],
            "close_order_id" : [], "close_date" : [],
            "close_price" : [], "close_order_type" : [],
        }
        df = pd.DataFrame(report_data)
        df.to_csv(self.file_name, mode="a", header=True, index=False)
        return

    '''
    report related:
    check wether content duplicated exists or not. if have same content,
    return True, if not return False
    '''
    def check_report_content_duplicated(self, report_data):
        df = pd.read_csv(self.file_name)
        past_entry_order_id = df["entry_order_id"].iloc[-1]
        recent_entry_order_id = report_data["entry_order_id"][0]
        past_close_order_id = df["close_order_id"].iloc[-1]
        recent_close_order_id = report_data["close_order_id"][0]

        if past_entry_order_id == recent_entry_order_id: return True
        if past_close_order_id == recent_close_order_id: return True
        return False

    ''' report related: convert timestamp to KST(Korea Standard Time) '''
    def change_korea_time(self, df):
        nine_hours = pd.Timedelta('9 hours')
        df['entry_date'] = pd.to_datetime(df['entry_date']) + nine_hours
        df['close_date'] = pd.to_datetime(df['close_date']) + nine_hours
        return df

    ''' report related: save report as csv file '''
    def report(self, report_data):
        self.csv_file_name()
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
