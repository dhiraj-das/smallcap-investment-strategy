import streamlit as st

from router import sidebar_menu

def run_UI():
    sidebar_menu()

if __name__ == '__main__':
    # url_params = st.query_params
    # if len(url_params.keys()) == 0:
    #     st.query_params["page"]="Home"
    #     url_params = st.query_params

    run_UI()