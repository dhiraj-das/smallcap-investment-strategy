import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_etl import ETLManager

from pyxirr import xirr 
from router import sidebar_menu

def run_UI():
    st.markdown('''
    #### :violet[Strategy 2: Invest + Pause SIP]
    ''')

    st.markdown('''
    Continuing from our previous discussion, the first investment strategy is to monitor the variation of the indices and take 
    investment decisions based on the following -
    1. Continue your SIP to invest X amount to the NIFTY SMALLCAP 250 TRI index when the variation is < +1σ. This essentially means that the index is undervalued
    and we can continue investing to this index.
    2. Pause your SIP if the Smallcase Index is > 1σ. This is because the index at such a scenario is overvalued and we can
    avoid buying units at a higher cost.
    ''')
    
    df = ETLManager().prepare_master_data()
    std_dev = df['relative_value'].std()
    fig1 = px.line(df, x='date', y='relative_value', color_discrete_sequence=["purple"])
    fig1.update_layout(xaxis_title='', yaxis_title=' Variation of the indices')
    fig1.update_layout(yaxis=dict(
        tickmode='array', 
        ticktext=['...', '+ 1σ','...'], 
        tickvals=[df['relative_value'].min(), 1+std_dev, df['relative_value'].max()])
    )
    fig1.update_traces(mode="lines", hovertemplate = "Date: %{x} <br>Ratio: %{y:.2f}", xhoverformat="%b %d, %Y")
    fig1.update_layout(hovermode="x unified")
    fig1.add_shape(type="rect", x0=df['date'].min(), x1=df['date'].max(), y0=df['relative_value'].min(), y1=1+std_dev,fillcolor="seagreen", opacity=0.2, line_width=1, label=dict(text="INVEST", textposition="middle center", font=dict(size=20)))
    fig1.add_shape(type="rect", x0=df['date'].min(), x1=df['date'].max(), y0=1+std_dev, y1=df['relative_value'].max(),fillcolor="maroon", opacity=0.1, line_width=1, label=dict(text="PAUSE", textposition="middle center", font=dict(size=20)))
    fig1.update_xaxes(dtick='M24', tickformat='%Y', ticklabelmode='period')
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown('''
    #### :violet[Estimation of Returns]
    ''')

    st.markdown('''
    Let us compare the returns using this strategy vis-à-vis investing in the NIFTY 50 and NIFTY Smallcap 250. For the sake of simplicity,
    we shall calculate the returns assuming an SIP of INR 10,000 made on a monthly basis.
    ''')

    ## Calculation of returns

    years = list(range(1, 15))
    largecap_returns = []
    smallcap_returns = []
    strategy1_returns = []
    for _, elt in enumerate(years):
        largecap = ETLManager().returns_from_nifty50(elt)
        smallcap = ETLManager().returns_from_nifty_smallcap250(elt)
        strategy1 = ETLManager().returns_from_strategy1(elt)
        largecap_returns.append(round(xirr(largecap)*100,1))
        smallcap_returns.append(round(xirr(smallcap)*100,1))
        strategy1_returns.append(round(xirr(strategy1)*100,1))
    returns_df = pd.DataFrame(zip(years, largecap_returns, smallcap_returns, strategy1_returns), columns=['Year','Nifty 50','Nifty Smallcap 250', 'Strategy 1'])
    # st.dataframe(returns_df)        

    fig2 = px.line(returns_df, x='Year', y=['Year','Nifty 50','Nifty Smallcap 250', 'Strategy 1'])
    fig2.update_layout(xaxis_title='Year', yaxis_title='XIRR %')
    fig2.update_layout(legend_title_text='Index / Strategy')
    fig2.update_layout(legend_traceorder="reversed")
    fig2.update_xaxes(showline=True, linewidth=1, linecolor='grey')
    fig2.update_yaxes(showline=True, linewidth=1, linecolor='grey')
    st.plotly_chart(fig2, use_container_width=True)
    
    # Navigation to Next Page Logic
    st.columns(3)[1].page_link("pages/strategy1.py", label='Navigate to Strategy 2', icon="♟️")

sidebar_menu()
run_UI()