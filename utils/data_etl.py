from datetime import datetime
import pandas as pd
import numpy as np
from utils.api_manager import NIFTYIndices

class ETLManager:
    def __init__(self):
        self._nifty50_df = NIFTYIndices('NIFTYINDEXTRI').get_nse_indices_returns("NIFTY 50","01-Apr-2005", datetime.today().strftime('%d-%b-%Y'), "NIFTY 50")
        self._smallcap250_df = NIFTYIndices('NIFTYINDEXTRI').get_nse_indices_returns("NIFTY SMALLCAP 250","01-Apr-2005", datetime.today().strftime('%d-%b-%Y'), "NIFTY SMALLCAP 250")

    def prepare_master_data(self):
        combined_df = self._nifty50_df.copy(deep=True)
        combined_df['small_tri'] = self._smallcap250_df['TotalReturnsIndex']
        combined_df = combined_df[['Date','TotalReturnsIndex', 'small_tri']]
        col_names = combined_df.columns
        new_cols = ['date', 'nifty50_tri', 'nifty_smallcap250_tri']
        combined_df.rename(columns=dict(zip(col_names, new_cols)), inplace=True)
        combined_df['date'] = pd.to_datetime(combined_df['date'], format='%d %b %Y')
        combined_df['nifty50_tri'] = pd.to_numeric(combined_df['nifty50_tri'])
        combined_df['nifty_smallcap250_tri'] = pd.to_numeric(combined_df['nifty_smallcap250_tri'])
        df_monthly = combined_df.groupby([combined_df['date'].dt.year, combined_df['date'].dt.month], as_index=False).first()
        df_monthly['largecap_rel_change'] = df_monthly['nifty50_tri']/df_monthly['nifty50_tri'].iloc[0]
        df_monthly['smallcap_rel_change'] = df_monthly['nifty_smallcap250_tri']/df_monthly['nifty_smallcap250_tri'].iloc[0]
        df_monthly['relative_value'] = df_monthly['smallcap_rel_change']/df_monthly['largecap_rel_change']
        return df_monthly
    
    def returns_from_nifty50(self, timeperiod = None):
        df = self.prepare_master_data()
        if timeperiod == None:
            subset_df = df.copy(deep=True)
        else:
            subset_df = df.tail(timeperiod*12)
        subset_df['condition'] = 'buy'
        subset_df['cashflow'] = np.where(subset_df['condition']=='buy', 10000, 0)
        subset_df['previous_nifty50_tri'] = subset_df['nifty50_tri'].shift(1)
        subset_df['tri_ratio'] = (subset_df['nifty50_tri'] / subset_df['previous_nifty50_tri'])
        subset_df['present_value'] = 10000
        subset_df = subset_df.reset_index(drop=True)
        for i in range(1, len(subset_df)):
            subset_df.loc[i, 'present_value'] = (subset_df.loc[i-1, 'present_value'] * subset_df.loc[i, 'tri_ratio']) + subset_df.loc[i, 'cashflow']
        final_df = pd.concat([subset_df, pd.DataFrame({'date': subset_df['date'].max(), 'cashflow': -(subset_df['present_value'].max())}, index=[len(subset_df)])])
        final_df = final_df[['date', 'cashflow']]
        return final_df
    
    def returns_from_nifty_smallcap250(self, timeperiod = None):
        df = self.prepare_master_data()
        if timeperiod == None:
            subset_df = df.copy(deep=True)
        else:
            subset_df = df.tail(timeperiod*12)
        subset_df['condition'] = 'buy'
        subset_df['cashflow'] = np.where(subset_df['condition']=='buy', 10000, 0)
        subset_df['previous_smallcap250_tri'] = subset_df['nifty_smallcap250_tri'].shift(1)
        subset_df['tri_ratio'] = (subset_df['nifty_smallcap250_tri'] / subset_df['previous_smallcap250_tri'])
        subset_df['present_value'] = 10000
        subset_df = subset_df.reset_index(drop=True)
        for i in range(1, len(subset_df)):
            subset_df.loc[i, 'present_value'] = (subset_df.loc[i-1, 'present_value'] * subset_df.loc[i, 'tri_ratio']) + subset_df.loc[i, 'cashflow']
        final_df = pd.concat([subset_df, pd.DataFrame({'date': subset_df['date'].max(), 'cashflow': -(subset_df['present_value'].max())}, index=[len(subset_df)])])
        final_df = final_df[['date', 'cashflow']]
        return final_df
    
    def returns_from_strategy1(self, timeperiod = None):
        df = self.prepare_master_data()
        std_dev = df['relative_value'].std()
        if timeperiod == None:
            subset_df = df.copy(deep=True)
        else:
            subset_df = df.tail(timeperiod*12)
        subset_df['condition'] = np.where(subset_df['relative_value']<(1+std_dev), 'buy', 'pause')
        subset_df['cashflow'] = np.where(subset_df['condition']=='buy', 10000, 0)
        subset_df['previous_smallcap250_tri'] = subset_df['nifty_smallcap250_tri'].shift(1)
        subset_df['tri_ratio'] = (subset_df['nifty_smallcap250_tri'] / subset_df['previous_smallcap250_tri'])
        subset_df['present_value'] = 10000
        subset_df = subset_df.reset_index(drop=True)
        for i in range(1, len(subset_df)):
            subset_df.loc[i, 'present_value'] = (subset_df.loc[i-1, 'present_value'] * subset_df.loc[i, 'tri_ratio']) + subset_df.loc[i, 'cashflow']
        final_df = pd.concat([subset_df, pd.DataFrame({'date': subset_df['date'].max(), 'cashflow': -(subset_df['present_value'].max())}, index=[len(subset_df)])])
        final_df = final_df[['date', 'cashflow']]
        return final_df
    
    def returns_from_strategy2(self, timeperiod = None):
        df = self.prepare_master_data()
        std_dev = df['relative_value'].std()
        if timeperiod == None:
            subset_df = df.copy(deep=True)
        else:
            subset_df = df.tail(timeperiod*12)
        subset_df['condition_s'] = np.where(subset_df['relative_value']<(1+std_dev), 'buy', 'pause')
        subset_df['condition_l'] = np.where(subset_df['relative_value']>(1+2*std_dev), 'buy', 'pause')
        subset_df['cashflow_s'] = np.where(subset_df['condition_s']=='buy', 10000, 0)
        subset_df['cashflow_l'] = np.where(subset_df['condition_l']=='buy', 10000, 0)
        subset_df['cashflow'] = subset_df['cashflow_s'] + subset_df['cashflow_l']
        subset_df['previous_smallcap250_tri'] = subset_df['nifty_smallcap250_tri'].shift(1)
        subset_df['previous_nifty50_tri'] = subset_df['nifty50_tri'].shift(1)
        subset_df['tri_ratio_s'] = (subset_df['nifty_smallcap250_tri'] / subset_df['previous_smallcap250_tri'])
        subset_df['tri_ratio_l'] = (subset_df['nifty50_tri'] / subset_df['previous_nifty50_tri'])
        subset_df['present_value_s'] = 10000
        subset_df['present_value_l'] = 0
        subset_df = subset_df.reset_index(drop=True)
        for i in range(1, len(subset_df)):
            subset_df.loc[i, 'present_value_s'] = (subset_df.loc[i-1, 'present_value_s'] * subset_df.loc[i, 'tri_ratio_s']) + subset_df.loc[i, 'cashflow_s']
            subset_df.loc[i, 'present_value_l'] = (subset_df.loc[i-1, 'present_value_l'] * subset_df.loc[i, 'tri_ratio_l']) + subset_df.loc[i, 'cashflow_l']
        final_df = pd.concat([subset_df, pd.DataFrame({'date': subset_df['date'].max(), 'cashflow': -(subset_df['present_value_s'].max()+subset_df['present_value_l'].max())}, index=[len(subset_df)])])
        final_df = final_df[['date', 'cashflow']]
        return final_df