import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.api_manager import NIFTYIndices

from pyxirr import xirr 
from router import sidebar_menu

# Data ETL
nifty50_df = pd.read_csv('data/nifty50_tri.csv', parse_dates=["Date"])
nifty250_df = pd.read_csv('data/nifty250_tri.csv', parse_dates=["Date"])
combined_df = nifty50_df.copy(deep=True)
combined_df['Smallcap_TRI'] = nifty250_df['Total Returns Index']
combined_df.index = pd.to_datetime(combined_df['Date'], format='%d %b %Y')
combined_df = combined_df.sort_index()
# df_monthly = combined_df.loc[combined_df.index == combined_df.index + pd.offsets.MonthEnd(0)]
df_monthly = combined_df.groupby([combined_df['Date'].dt.year, combined_df['Date'].dt.month], as_index=False).last()
df_monthly.index = pd.to_datetime(df_monthly['Date'], format='%d %b %Y')


df_monthly['Smallcap_rel_change'] = df_monthly['Smallcap_TRI']/df_monthly['Smallcap_TRI'].iloc[0]
df_monthly['Largecap_rel_change'] = combined_df['Total Returns Index']/df_monthly['Total Returns Index'].iloc[0]
df_monthly['Rel_value'] = df_monthly['Smallcap_rel_change']/df_monthly['Largecap_rel_change']

std = df_monthly['Rel_value'].std()

def run_UI():
    st.markdown('''
    #### :violet[Strategy 1: Invest + Pause SIP]
    ''')

    st.markdown('''
    Continuing from our previous discussion, the first investment strategy is to monitor the variation of the indices and take 
    investment decisions based on the following -
    1. Continue your SIP to invest X amount to the NIFTY SMALLCAP 250 TRI index when the variation is < +1σ. This essentially means that the index is undervalued
    and we can continue investing to this index.
    2. Pause your SIP if the Smallcase Index is > 1σ. This is because the index at such a scenario is overvalued and we can
    avoid buying units at a higher cost.
    ''')

    fig1 = px.line(df_monthly, x='Date', y='Rel_value', color_discrete_sequence=["purple"])
    fig1.update_layout(xaxis_title='', yaxis_title=' Variation of the indices')
    fig1.update_layout(yaxis=dict(
        tickmode='array', 
        ticktext=['...', '+ 1σ','...'], 
        tickvals=[df_monthly['Rel_value'].min(), 1+std, df_monthly['Rel_value'].max()])
    )
    fig1.update_traces(mode="lines", hovertemplate = "Date: %{x} <br>Ratio: %{y:.2f}", xhoverformat="%b %d, %Y")
    fig1.update_layout(hovermode="x unified")
    fig1.add_shape(type="rect", x0=df_monthly['Date'].min(), x1=df_monthly['Date'].max(), y0=df_monthly['Rel_value'].min(), y1=1+std,fillcolor="seagreen", opacity=0.2, line_width=1, label=dict(text="INVEST", textposition="middle center", font=dict(size=20)))
    fig1.add_shape(type="rect", x0=df_monthly['Date'].min(), x1=df_monthly['Date'].max(), y0=1+std, y1=df_monthly['Rel_value'].max(),fillcolor="maroon", opacity=0.1, line_width=1, label=dict(text="PAUSE", textposition="middle center", font=dict(size=20)))
    fig1.update_xaxes(dtick='M24', tickformat='%Y', ticklabelmode='period')
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown('''
    #### :violet[Estimation of Returns]
    ''')

    st.markdown('''
    Let us compare the returns using this strategy vis-à-vis investing in the NIFTY 50 and NIFTY Smallcap 250. For the sake of simplicity,
    we shall calculate the returns assuming an SIP of INR 10,000 made on a monthly basis.
    ''')

    ## Calculation of nifty50 returns
    returns = []
    df_monthly['nifty50_condition'] = 'buy'
    df_monthly['nifty50_cashflow'] = np.where(df_monthly['nifty50_condition']=='buy', 10000, 0)
    df_monthly['nifty50_tri_prev'] = df_monthly['Total Returns Index'].shift(1)
    df_monthly['nifty50_tri_ratio'] = (df_monthly['Total Returns Index'] / df_monthly['nifty50_tri_prev'])
    df_monthly['nifty50_pv'] = 10000
    xir_df = df_monthly.reset_index(drop=True)
    for i in range(1, len(xir_df)):
        xir_df.loc[i, 'nifty50_pv'] = (xir_df.loc[i-1, 'nifty50_pv'] * xir_df.loc[i, 'nifty50_tri_ratio']) + xir_df.loc[i, 'nifty50_cashflow']
    cal_df = pd.concat([xir_df, pd.DataFrame({'Date': xir_df['Date'].max(), 'nifty50_cashflow': -(xir_df['nifty50_pv'].max())}, index=[len(xir_df)])])
    xir_df = cal_df[['Date', 'nifty50_cashflow']]
    returns.append(round(xirr(xir_df['Date'], xir_df['nifty50_cashflow'])*100,2))
    # st.markdown(returns*100)

    ## Calculation of smallcap250 returns
    df_monthly['smallcap_condition'] = 'buy'
    df_monthly['smallcap_cashflow'] = np.where(df_monthly['smallcap_condition']=='buy', 10000, 0)
    df_monthly['smallcap_tri_prev'] = df_monthly['Smallcap_TRI'].shift(1)
    df_monthly['smallcap_tri_ratio'] = (df_monthly['Smallcap_TRI'] / df_monthly['smallcap_tri_prev'])
    df_monthly['smallcap_pv'] = 10000
    xir_df = df_monthly.reset_index(drop=True)
    for i in range(1, len(xir_df)):
        xir_df.loc[i, 'smallcap_pv'] = (xir_df.loc[i-1, 'smallcap_pv'] * xir_df.loc[i, 'smallcap_tri_ratio']) + xir_df.loc[i, 'smallcap_cashflow']
    cal_df = pd.concat([xir_df, pd.DataFrame({'Date': xir_df['Date'].max(), 'smallcap_cashflow': -(xir_df['smallcap_pv'].max())}, index=[len(xir_df)])])
    xir_df = cal_df[['Date', 'smallcap_cashflow']]
    returns.append(round(xirr(xir_df['Date'], xir_df['smallcap_cashflow'])*100,2))
    # st.markdown(returns*100)

    ## Calculation of scenario1 returns
    df_monthly['scen1_condition'] = np.where(df_monthly['Rel_value']>(1+std), 'buy', 'pause')
    df_monthly['scen1_cashflow'] = np.where(df_monthly['scen1_condition']=='buy', 10000, 0)
    df_monthly['smallcap_tri_prev'] = df_monthly['Smallcap_TRI'].shift(1)
    df_monthly['smallcap_tri_ratio'] = (df_monthly['Smallcap_TRI'] / df_monthly['smallcap_tri_prev'])
    df_monthly['scen1_pv'] = 10000
    xir_df = df_monthly.reset_index(drop=True)
    for i in range(1, len(xir_df)):
        xir_df.loc[i, 'scen1_pv'] = (xir_df.loc[i-1, 'scen1_pv'] * xir_df.loc[i, 'smallcap_tri_ratio']) + xir_df.loc[i, 'scen1_cashflow']
    cal_df = pd.concat([xir_df, pd.DataFrame({'Date': xir_df['Date'].max(), 'scen1_cashflow': -(xir_df['scen1_pv'].max())}, index=[len(xir_df)])])
    xir_df = cal_df[['Date', 'scen1_cashflow']]
    returns.append(round(xirr(xir_df['Date'], xir_df['scen1_cashflow'])*100,2))
    # st.dataframe(cal_df)
    
    x = ['NIFTY50', 'SMALLCAP 250', 'Strategy 1']

    # Use the hovertext kw argument for hover text
    fig2 = go.Figure(data=[go.Bar(x=x, y=returns, text=returns, textposition='auto')])
    # Customize aspect
    fig2.update_traces(marker_color='rgb(158,202,225)', marker_line_color='rgb(8,48,107)',
                    marker_line_width=1.5, opacity=0.4)
    fig2.update_layout(title_text='XIRR of the different scenarios for the entire period')
    st.plotly_chart(fig2, use_container_width=True)

    # a = NIFTYIndices('NIFTYINDEXTRI').get_nse_indices_returns("NIFTY 50","01-Jan-2024", "15-Jan-2024", "NIFTY 50")
    # st.dataframe(a)

    st.columns(3)[1].page_link("pages/strategy1.py", label='Navigate to Strategy 2', icon="♟️")

sidebar_menu()
run_UI()