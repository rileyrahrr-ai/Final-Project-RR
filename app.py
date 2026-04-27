import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Financial Analysis Dashboard", layout="wide")

# =========================================================
# Sidebar Inputs
# =========================================================
st.sidebar.title("Settings")

# ----- Stock Input -----
st.sidebar.subheader("Individual Stock Analysis")
stock_ticker = st.sidebar.text_input("Enter Stock Ticker", "AAPL").upper()

# ----- Portfolio Input -----
st.sidebar.subheader("Portfolio Settings")
portfolio_input = st.sidebar.text_input(
    "Enter 5 stock tickers (space-separated)",
    "AAPL MSFT AMZN GOOG NVDA"
)
portfolio_tickers = portfolio_input.upper().split()

# Equal weights for simplicity
weights = np.array([1/len(portfolio_tickers)] * len(portfolio_tickers))

benchmark = "SPY"


# =========================================================
# PART 1: Individual Stock Analysis
# =========================================================
st.title("📈 Financial Analysis Dashboard")
st.header("Part 1: Individual Stock Analysis")

try:
    data = yf.download(stock_ticker, period="6mo", interval="1d")

    # Moving averages
    data["20MA"] = data["Close"].rolling(20).mean()
    data["50MA"] = data["Close"].rolling(50).mean()

    price = data["Close"].iloc[-1]
    ma20 = data["20MA"].iloc[-1]
    ma50 = data["50MA"].iloc[-1]

    # Trend
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
        rsi_status = "Overbought (Sell Signal)"
    elif rsi_val < 30:
        rsi_status = "Oversold (Buy Signal)"
    else:
        rsi_status = "Neutral"

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
    if trend == "Strong Uptrend" and rsi_status != "Overbought (Sell Signal)":
        recommendation = "BUY"
    elif trend == "Strong Downtrend" and rsi_status != "Oversold (Buy Signal)":
        recommendation = "SELL"
    else:
        recommendation = "HOLD"

    # Display results
    st.subheader(f"Results for {stock_ticker}")
    st.write(f"**Trend:** {trend}")
    st.write(f"**RSI:** {rsi_val:.2f} → {rsi_status}")
    st.write(f"**Volatility:** {vol_val:.2%} ({vol_class})")
    st.write(f"### Final Recommendation: **{recommendation}**")

    # Plot
    st.subheader("Trend Chart")
    st.line_chart(data[["Close", "20MA", "50MA"]])

except Exception as e:
    st.error("Error loading stock data. Please check the ticker and try again.")


# =========================================================
# PART 2: Portfolio Performance Dashboard
# =========================================================
st.header("Part 2: Portfolio Performance")

try:
    # Download data
    prices = yf.download(portfolio_tickers, period="1y")["Adj Close"]
    benchmark_price = yf.download(benchmark, period="1y")["Adj Close"]

    # Returns
    returns = prices.pct_change().dropna()
    portfolio_returns = (returns * weights).sum(axis=1)
    benchmark_returns = benchmark_price.pct_change().dropna()

    # Metrics
    total_return = (1 + portfolio_returns).prod() - 1
    benchmark_return = (1 + benchmark_returns).prod() - 1
    outperformance = total_return - benchmark_return

    vol = portfolio_returns.std() * np.sqrt(252)
    sharpe = (portfolio_returns.mean() * 252) / (portfolio_returns.std() * np.sqrt(252))

    # Display results
    st.subheader("Portfolio Metrics")
    st.write(f"**Portfolio Total Return:** {total_return:.2%}")
    st.write(f"**SPY Benchmark Return:** {benchmark_return:.2%}")
    st.write(f"**Outperformance:** {outperformance:.2%}")
    st.write(f"**Annualized Volatility:** {vol:.2%}")
    st.write(f"**Sharpe Ratio:** {sharpe:.2f}")

    # Plot comparison
    st.subheader("Cumulative Return Comparison")
    cum_returns = pd.DataFrame({
        "Portfolio": (1 + portfolio_returns).cumprod(),
        "SPY": (1 + benchmark_returns).cumprod()
    })
    st.line_chart(cum_returns)

except Exception as e:
    st.error("Error loading portfolio data. Please check the tickers.")
