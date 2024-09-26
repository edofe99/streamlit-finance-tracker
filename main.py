import streamlit as st
import functions.finance_tracker as finance_tracker
import pandas as pd

# -------------------------------- Page config ------------------------------- #
st.set_page_config(page_title='Finance Tracker',initial_sidebar_state='collapsed',layout='wide')

# ---------------------------------------------------------------------------- #
#                                   Main App                                   #
# ---------------------------------------------------------------------------- #

st.markdown('# Finance Tracker')
if 'data' not in st.session_state:
    st.session_state.data = pd.read_csv('./assets/test_data.csv')
    st.session_state.data['Date'] =  pd.to_datetime(st.session_state.data['Date'])



    # All app is created inside the finance_tracker.py file in order to keep
    # this one clean and small
    
finance_tracker.main_dashboard()


# Prevent from swithing tab view when pressing a button
if "initial_rerun_done" not in st.session_state:
    st.session_state.initial_rerun_done = True
    st.rerun()
