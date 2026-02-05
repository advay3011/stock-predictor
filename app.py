import streamlit as st

# import your backend agent
from stock_predictor_agent import run_prediction   # change if your function name differs

st.set_page_config(page_title="Stock Predictor Agent")

st.title("📈 Stock Predictor Agent")

ticker = st.text_input("Enter stock ticker (ex: AAPL)")
horizon = st.slider("Prediction horizon (days)", 1, 30, 7)

if st.button("Run Prediction"):
    if not ticker:
        st.warning("Please enter a ticker.")
    else:
        with st.spinner("Analyzing..."):
            result = run_prediction(ticker, horizon)   # calls your agent

        st.subheader("Prediction Result")
        st.write(result)
