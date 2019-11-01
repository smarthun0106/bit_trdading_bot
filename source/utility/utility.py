import sys
from os import path
sys.path.append(path.dirname(path.dirname( path.abspath(__file__))))
from settings import TELEGRAM_ERROR_BOT_TOKEN, TELEGRAM_REPORT_BOT_TOKEN

from datetime import datetime
import pandas as pd
import requests

class Utils(object):
    ''' make standard time clearer '''
    def time_now(self):
        dt = datetime.now()
        time_now = dt.strftime('%Y-%m-%d %H:%M:%S.%f')
        return time_now[:-7]

    ''' telegram related: get url path included token '''
    def telegram_url_path(self, token):
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

        url_path = self.telegram_url_path(token)
        parameters = { "chat_id" : "756052880", "text" : text }
        r = requests.get(url_path, params=parameters)
        return r
