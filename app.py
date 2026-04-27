import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.title("📈 Financial Analysis Dashboard")

st.sidebar.header("User Inputs")

# ----- Stock Input -----
ticker = st.sidebar.text_input("Stock Ticker", "AAPL")

# ----- Portfolio Input -----
st.sidebar.subheader("Portfolio Ticketers")
default = "AAPL MSFT AMZN GOOG NVDA"
portfolio_input = st.sidebar.text_input("Enter 5 tickers (space-separated)", default)
portfolio = portfolio_input.upper().split()

# Fixed equal weights for simplicity
weights = np.array([1/len(portfolio)] * len(portfolio))

# Benchmark
benchmark = "SPY"

st.header("Part 1: Individual Stock Analysis")

# Download data
data = yf.download(ticker, period="6mo", interval="1d")

# Trend analysis
data["20MA"] = data["Close"].rolling(20).mean()
data["50MA"] = data["Close"].rolling(50).mean()

price = data["Close"].iloc[-1]
ma20 = data["20MA"].iloc[-1]
ma50 = data["50MA"].iloc[-1]

if price > ma20 > ma50:
    trend = "Strong Uptrend"
elif price < ma20 < ma50:
    trend = "Strong Downtrend"
else:
    trend = "Mixed Trend"

# RSI
delta = data["Close"].diff()
gain = delta.clip(lower=0)
loss = -delta.clip(upper=0)
avg_gain = gain.rolling(14).mean()
avg_loss = loss.rolling(14).mean()
rs = avg_gain / avg_loss
data["RSI"] = 100 - (100 / (1 + rs))

rsi_val = data["RSI"].iloc[-1]

if rsi_val > 70:
    rsi_sig = "Overbought (Sell Signal)"
elif rsi_val < 30:
    rsi_sig = "Oversold (Buy Signal)"
else:
    rsi_sig = "Neutral"

# Volatility
data["Return"] = data["Close"].pct_change()
vol = data["Return"].rolling(20).std() * np.sqrt(252)
vol_val = vol.iloc[-1]

if vol_val > 0.40:
    vol_class = "High"
elif vol_val >= 0.25:
    vol_class = "Medium"
else:
    vol_class = "Low"

# Recommendation
if trend == "Strong Uptrend" and rsi_sig != "Overbought (Sell Signal)":
    reco = "BUY"
elif trend == "Strong Downtrend" and rsi_sig != "Oversold (Buy Signal)":
    reco = "SELL"
else:
    reco = "HOLD"

# Display
st.subheader(f"Results for {ticker}")
st.write(f"Trend: {trend}")
st.write(f"RSI: {rsi_val:.2f} → {rsi_sig}")
st.write(f"Volatility: {vol_val:.2%} ({vol_class})")
st.write(f"Recommendation: **{reco}**")

# Plot
st.line_chart(data[["Close", "20MA", "50MA"]])

# ---- PART 2 ----
st.header("Part 2: Portfolio Performance")

prices = yf.download(portfolio, period="1y")["Adj Close"]
benchmark_price = yf.download(benchmark, period="1y")["Adj Close"]

returns = prices.pct_change().dropna()
portfolio_returns = (returns * weights).sum(axis=1)
benchmark_returns = benchmark_price.pct_change().dropna()

total_return = (1 + portfolio_returns).prod() - 1
benchmark_return = (1 + benchmark_returns).prod() - 1
outperformance = total_return - benchmark_return
vol = portfolio_returns.std() * np.sqrt(252)
sharpe = (portfolio_returns.mean() * 252) / (portfolio_returns.std() * np.sqrt(252))

# Display
st.write(f"Portfolio Return: {total_return:.2%}")
st.write(f"SPY Return: {benchmark_return:.2%}")
st.write(f"Outperformance: {outperformance:.2%}")
st.write(f"Volatility: {vol:.2%}")
st.write(f"Sharpe Ratio: {sharpe:.2f}")

# Plot
st.line_chart(
    pd.DataFrame({
        "Portfolio": (1 + portfolio_returns).cumprod(),
        "SPY": (1 + benchmark_returns).cumprod()
    })
)
