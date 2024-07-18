import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Data ETL
nifty50_df = pd.read_csv('data/nifty50_tri.csv')
nifty250_df = pd.read_csv('data/nifty250_tri.csv')
combined_df = nifty50_df.copy(deep=True)
combined_df['Smallcap_TRI'] = nifty250_df['Total Returns Index']
combined_df.index = pd.to_datetime(combined_df['Date'], format='%d %b %Y')

# Code for the GUI of the app goes here
st.title("📈 Smallcap Investment Strategy")
st.write(
    "An investment strategy for investing into smallcap"
)

st.dataframe(combined_df)

fig = px.line(combined_df, x='Date', y=['Total Returns Index', 'Smallcap_TRI'], color_discrete_sequence=["#0514C0"], labels={'y': 'TRI'})
fig.update_layout(xaxis=dict(autorange="reversed"))
fig.update_layout(title='NIFTY 50 TRI', xaxis_title='Date', yaxis_title='TRI')

st.plotly_chart(fig, use_container_width=True)