import streamlit as st
from stock_predictor_agent import run_prediction

st.title("\U0001f4c8 Stock Predictor Agent")

ticker = st.text_input("Stock ticker (AAPL, TSLA, NVDA)")
days = st.slider("Days of history", 5, 60, 30)

if st.button("Analyze"):
    if ticker:
        with st.spinner("Agent analyzing..."):
            result = run_prediction(ticker, days)
        st.write(result)
