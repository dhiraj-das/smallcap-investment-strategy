import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils.data_etl import ETLManager

from pyxirr import xirr 
from router import sidebar_menu

def run_UI():
    st.markdown('''
    #### :violet[Strategy 1: Invest + Pause]
    ''')

    st.markdown('''
    Continuing from our previous discussion, the first investment strategy is to monitor the variation of the indices and take 
    investment decisions based on the following -
    1. Continue your SIP to invest X amount to the Smallcap Index when the variation is < +1σ. This essentially means that the index is undervalued
    and we can continue investing to this index.
    2. Pause your SIP if the variation is > 1σ. This is because the Smallcap index at such a scenario is overvalued and we can
    avoid buying units at a higher cost.
    ''')
    
    df = ETLManager().prepare_master_data()
    std_dev = df['relative_value'].std()
    fig1 = px.line(df, x='date', y='relative_value', color_discrete_sequence=["purple"])
    fig1.update_layout(xaxis_title='', yaxis_title=' Variation of the indices')
    fig1.update_layout(yaxis=dict(
        tickmode='array', 
        ticktext=['...', '1', '+ 1σ','...'], 
        tickvals=[df['relative_value'].min(), 1, 1+1*std_dev, df['relative_value'].max()]
    ))
    fig1.update_traces(mode="lines", hovertemplate = "Date: %{x} <br>Ratio: %{y:.2f}", xhoverformat="%b %d, %Y")
    fig1.update_layout(hovermode="x unified")
    fig1.add_shape(type="rect", x0=df['date'].min(), x1=df['date'].max(), y0=df['relative_value'].min(), y1=1+1*std_dev,fillcolor="seagreen", opacity=0.2, line_width=1, label=dict(text="INVEST", textposition="middle center", font=dict(size=20)))
    fig1.add_shape(type="rect", x0=df['date'].min(), x1=df['date'].max(), y0=1+1*std_dev, y1=df['relative_value'].max(),fillcolor="maroon", opacity=0.1, line_width=1, label=dict(text="PAUSE", textposition="middle center", font=dict(size=20)))
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

    years = [3, 5, 7, 10, 12, 15]
    largecap_returns = []
    smallcap_returns = []
    strategy1_returns = []
    largecap_inv = []
    smallcap_inv = []
    strategy1_inv = []
    for _, elt in enumerate(years):
        largecap = ETLManager().returns_from_nifty50(elt)
        smallcap = ETLManager().returns_from_nifty_smallcap250(elt)
        strategy1 = ETLManager().returns_from_strategy1(elt)
        largecap_returns.append(round(xirr(largecap)*100,1))
        smallcap_returns.append(round(xirr(smallcap)*100,1))
        strategy1_returns.append(round(xirr(strategy1)*100,1))
        largecap_inv.append(largecap.iloc[:-1]['cashflow'].sum())
        smallcap_inv.append(smallcap.iloc[:-1]['cashflow'].sum())
        strategy1_inv.append(strategy1.iloc[:-1]['cashflow'].sum())

    st.markdown('''
    ###### :violet[Amount Invested]
    ''')

    fig2 = go.Figure(data=[
        go.Bar(name='Nifty 50', x=years, y=largecap_inv, marker_color='grey'),
        go.Bar(name='Nifty Smallcap 250', x=years, y=smallcap_inv, marker_color='lightslategray'),
        go.Bar(name='Strategy 2', x=years, y=strategy1_inv, marker_color='palevioletred')
        
    ])
    fig2.update_layout(barmode='group')
    x_vals = ['3 years','5 years','7 years', '10 years', '12 years','15 years']
    fig2.update_layout(xaxis=dict(
        tickmode='array', 
        ticktext=x_vals, 
        tickvals=years)
    )
    fig2.update_layout(bargroupgap=0.2)
    fig2.update_layout(legend = {"orientation": "h", "xanchor": "center", "x": 0.5})
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown('''
    ###### :violet[XIRR]
    ''')

    fig2 = go.Figure(data=[
        go.Bar(name='Nifty 50', x=years, y=largecap_returns, marker_color='grey'),
        go.Bar(name='Nifty Smallcap 250', x=years, y=smallcap_returns, marker_color='lightslategray'),
        go.Bar(name='Strategy 2', x=years, y=strategy1_returns, marker_color='palevioletred')
        
    ])
    fig2.update_layout(barmode='group')
    x_vals = ['3 years','5 years','7 years', '10 years', '12 years','15 years']
    fig2.update_layout(xaxis=dict(
        tickmode='array', 
        ticktext=x_vals, 
        tickvals=years)
    )
    fig2.update_layout(bargroupgap=0.2)
    fig2.update_layout(legend = {"orientation": "h", "xanchor": "center", "x": 0.5})
    st.plotly_chart(fig2, use_container_width=True)
    
    # Navigation to Next Page Logic
    _, middle, _ = st.columns(3)
    if middle.button("Navigate to Strategy 2", use_container_width=True):
        st.toast('Watch out this space for the upcoming strategies!', icon='🎉')
    # st.columns(3)[1].page_link("pages/strategy1.py", label='Navigate to Strategy 2', icon="♟️")

sidebar_menu()
run_UI()