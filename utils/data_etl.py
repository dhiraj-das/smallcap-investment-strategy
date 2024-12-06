from datetime import datetime
import pandas as pd
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