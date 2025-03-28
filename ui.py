import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from data_loader import load_data
from backtester import apply_indicators

st.set_page_config(page_title="AI Trader", layout="wide", page_icon="📈")

st.markdown("<h1 style='color:white;'>📊 AI Trader Dashboard</h1>", unsafe_allow_html=True)

# Simple metrics
col1, col2 = st.columns(2)
with col1:
    st.metric("Strategy Used", "Best from strategy_evolver")
    st.metric("Symbol", "XAUUSD")

with col2:
    st.metric("Timeframe", "M5")
    st.metric("Risk per Trade", "1%")

# Load and display chart
st.markdown("### 📈 Market Chart with Indicators")
data = load_data("XAUUSD.", days_back=3)
data = apply_indicators(data)

fig = go.Figure(data=[
    go.Candlestick(
        x=data['time'],
        open=data['open'],
        high=data['high'],
        low=data['low'],
        close=data['close'],
        name="Candles"
    ),
    go.Scatter(x=data['time'], y=data['ema'], mode='lines', name='EMA 20', line=dict(color='cyan')),
    go.Scatter(x=data['time'], y=data['ema_fast'], mode='lines', name='EMA 10', line=dict(color='orange')),
    go.Scatter(x=data['time'], y=data['ema_slow'], mode='lines', name='EMA 50', line=dict(color='white'))
])

fig.update_layout(
    xaxis_rangeslider_visible=False,
    template="plotly_dark",
    height=600
)

st.plotly_chart(fig, use_container_width=True)
