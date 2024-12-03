import streamlit as st

from router import sidebar_menu

def run_UI():
    sidebar_menu()
    st.switch_page("pages/home.py")

if __name__ == '__main__':
    run_UI()