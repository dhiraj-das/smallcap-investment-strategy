import configparser
import os
import streamlit as st
import requests
from requests import HTTPError
import pandas as pd
import json
import datetime

class NIFTYIndices:
    def __init__(_self, API):
        config = configparser.ConfigParser()
        config.read(os.path.dirname(__file__) + '/conf.ini')
        _self.url = config.get(API, 'url')
        _self.header = {
            'Connection': 'keep-alive',
            'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'DNT': '1',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua-mobile': '?0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
            'Content-Type': 'application/json; charset=UTF-8',
            'Origin': 'https://niftyindices.com',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://niftyindices.com/reports/historical-data',
            'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8',
        }
    
    @st.cache_data
    def _index_total_returns(_self, symbol, start_date, end_date, index_name):
        start_date = datetime.datetime.strptime(start_date, "%d-%b-%Y").strftime("%d-%b-%Y")
        end_date = datetime.datetime.strptime(end_date, "%d-%b-%Y").strftime("%d-%b-%Y")
        data = {"cinfo": f"{{'name':'{symbol}','startDate':'{start_date}','endDate':'{end_date}','indexName':'{index_name}'}}"}

        request = requests.post(_self.url, headers=_self.header, json=data)
        payload = request.json()
        payload = json.loads(payload["d"])
        if not payload:
            request.raise_for_status()
        
        payload=pd.DataFrame.from_records(payload)
        return payload

    def get_nse_indices_returns(_self, symbol, start_date, end_date, index_name):
        try:
            historical_returns_data = _self._index_total_returns(symbol, start_date, end_date, index_name)
            return historical_returns_data
        except HTTPError as e:
            raise e
