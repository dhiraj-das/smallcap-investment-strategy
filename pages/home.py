import streamlit as st
import pandas as pd
import plotly.express as px

from router import sidebar_menu

# Pandas options
pd.options.display.max_rows = 25
pd.options.display.max_columns = 12
pd.options.display.expand_frame_repr = True
pd.options.display.large_repr = 'truncate'
pd.options.display.float_format = '{:.2f}'.format

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

# Code for the GUI of the app goes here
def run_UI():
    st.markdown('''
    #### :violet[Background]
    ''')

    st.markdown('''
    Due to the financial maturity of large-cap companies, these stocks are considered a low-risk, safer bet
    when market conditions are choppy.
    Small-cap companies, on the other hand, require a more tactical approach for investing into.
    
    Depending on the timing of market entry, based on the relative valuation of small-cap vis-à-vis large-cap,
    investors have a potential to make higher returns than merely tracking the small-cap index.
    ''')

    st.markdown('''
    #### :violet[Hypothesis]
    ''')

    st.markdown('''
    We explore this hypothesis based on a relative valuation of the NIFTY 50 TRI and 
    NIFTY SMALLCAP 250 TRI.
    ''')

    with st.expander("See Detailed Calculations"):
        st.write('''
            1. The values for both indexes on April 2005 has been selected as a base.
            2. The relative change of the following monthly values have been calculated from the base month.
            For example, relative change for nifty smallcap 250 TRI on July 2023 = Value on July 2023 / Value on April 2005.
            This relative change has been calculated for both indexes for each month.
            3. Finally, the ratio of the relative change in the Smallcap TRI to the Largecap TRI is calculated and plotted.
        ''')

    st.markdown('''
    The ratio of the returns from the NIFTY SMALLCAP 250 TRI and NIFTY 50 TRI from April 2005 is represented in the chart below.
    ''')
    
    fig = px.line(df_monthly, x='Date', y='Rel_value', color_discrete_sequence=["purple"])
    fig.update_layout(xaxis_title='', yaxis_title=' Ratio of the indices')
    fig.update_traces(mode="lines", hovertemplate = "Date: %{x} <br>Ratio: %{y:.2f}", xhoverformat="%b %d, %Y")
    fig.update_layout(hovermode="x unified")
    fig.update_xaxes(dtick='M24', tickformat='%Y', ticklabelmode='period')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('''
    The chart below highlights the regions within ±1σ, ±2σ, and ±3σ of the ratio of relative change of the indices. Based on which, we shall
    try to formulate certain investment strategies.
    ''')
    
    fig2 = px.line(df_monthly, x='Date', y='Rel_value', color_discrete_sequence=["purple"])
    fig2.update_layout(xaxis_title='', yaxis_title=' Variation of the indices')
    fig2.update_layout(yaxis=dict(
        tickmode='array', 
        ticktext=['- 3σ','- 2σ','- 1σ', '1', '+ 1σ','+ 2σ','+ 3σ'], 
        tickvals=[1-3*std, 1-2*std, 1-std, 1, 1+std, 1+2*std, 1+3*std])
    )
    fig2.update_traces(mode="lines", hovertemplate = "Date: %{x} <br>Ratio: %{y:.2f}", xhoverformat="%b %d, %Y")
    fig2.update_layout(hovermode="x unified")
    fig2.add_shape(type="rect", x0=df_monthly['Date'].min(), x1=df_monthly['Date'].max(), y0=1-std, y1=1+std,fillcolor="blue", opacity=0.15, line_width=1)
    fig2.add_shape(type="rect", x0=df_monthly['Date'].min(), x1=df_monthly['Date'].max(), y0=1-2*std, y1=1+2*std,fillcolor="blue", opacity=0.1, line_width=1)
    fig2.add_shape(type="rect", x0=df_monthly['Date'].min(), x1=df_monthly['Date'].max(), y0=1-3*std, y1=1+3*std,fillcolor="blue", opacity=0.05, line_width=1)
    fig2.update_xaxes(dtick='M24', tickformat='%Y', ticklabelmode='period')
    st.plotly_chart(fig2, use_container_width=True)

    st.columns(3)[1].page_link("pages/strategy1.py", label='Navigate to Strategy 1', icon="♟️")

sidebar_menu()
run_UI()
