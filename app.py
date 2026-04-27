import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Final Project App", layout="wide")

# =============================================================
# Custom CSS for green and yellow borders around charts
# =============================================================
st.markdown("""
<style>
.chart-box-green {
    border: 5px solid #00cc44;
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 25px;
}
.chart-box-yellow {
    border: 5px solid #ffeb3b;
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 25px;
}
</style>
""", unsafe_allow_html=True)

# =============================================================
# SIDEBAR INPUTS
# =============================================================
st.sidebar.title("Input Settings")

# --- Part 1 Stock Input ---
st.sidebar.subheader("Individual Stock Analysis")
stock = st.sidebar.text_input("Enter a stock ticker:", "AAPL").upper()

# --- Part 2 Portfolio Input ---
st.sidebar.subheader("Portfolio Tickers (5 Stocks)")
portfolio_raw = st.sidebar.text_input("Enter 5 tickers (space separated):", "AAPL MSFT AMZN GOOG NVDA")
portfolio_list = portfolio_raw.upper().split()
if len(portfolio_list) != 5:
    st.sidebar.warning("Please enter exactly 5 tickers.")

weights = np.array([1/5] * 5)
benchmark = "SPY"


# =============================================================
# PART 1 — INDIVIDUAL STOCK ANALYSIS
# =============================================================
st.title("📈 Final Project Financial Dashboard")
st.header("Part 1: Individual Stock Analysis")

try:
    # Step 1: Data Collection
    data = yf.download(stock, period="6mo", interval="1d")

    # Step 2: Trend Analysis
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

    # Step 3: Momentum (RSI)
    delta = data["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss
    data["RSI"] = 100 - (100 / (1 + rs))
    rsi_val = data["RSI"].iloc[-1]

    if rsi_val > 70:
        rsi_signal = "Overbought (Sell Signal)"
    elif rsi_val < 30:
        rsi_signal = "Oversold (Buy Signal)"
    else:
        rsi_signal = "Neutral"

    # Step 4: Volatility
    data["Returns"] = data["Close"].pct_change()
    vol = data["Returns"].rolling(20).std() * np.sqrt(252)
    vol_val = vol.iloc[-1]

    if vol_val > 0.40:
        vol_class = "High"
    elif vol_val >= 0.25:
        vol_class = "Medium"
    else:
        vol_class = "Low"

    # Step 5: Recommendation
    if trend == "Strong Uptrend" and rsi_signal != "Overbought (Sell Signal)":
        recommendation = "BUY"
    elif trend == "Strong Downtrend" and rsi_signal != "Oversold (Buy Signal)":
        recommendation = "SELL"
    else:
        recommendation = "HOLD"

    st.subheader(f"Results for {stock}")
    st.write(f"**Trend:** {trend}")
    st.write(f"**RSI:** {rsi_val:.2f} → {rsi_signal}")
    st.write(f"**Volatility:** {vol_val:.2%} ({vol_class})")
    st.write(f"### Final Recommendation: **{recommendation}**")

    # Chart
    st.markdown('<div class="chart-box-green">', unsafe_allow_html=True)
    st.subheader("Price with Moving Averages")

    fig, ax = plt.subplots(figsize=(10,4))
    ax.plot(data["Close"], label="Close Price")
    ax.plot(data["20MA"], label="20MA")
    ax.plot(data["50MA"], label="50MA")
    ax.legend()
    st.pyplot(fig)
    st.markdown("</div>", unsafe_allow_html=True)

except Exception as e:
    st.error("Error retrieving stock data. Check ticker symbol.")


# =============================================================
# PART 2 — PORTFOLIO PERFORMANCE DASHBOARD
# =============================================================
st.header("Part 2: Portfolio Performance Dashboard")

try:
    prices = yf.download(portfolio_list, period="1y")["Adj Close"]
    benchmark_price = yf.download(benchmark, period="1y")["Adj Close"]

    returns = prices.pct_change().dropna()
    portfolio_returns = (returns * weights).sum(axis=1)
    benchmark_returns = benchmark_price.pct_change().dropna()

    total_return = (1 + portfolio_returns).prod() - 1
    benchmark_return = (1 + benchmark_returns).prod() - 1
    outperformance = total_return - benchmark_return
    volatility = portfolio_returns.std() * np.sqrt(252)
    sharpe = (portfolio_returns.mean() * 252) / (portfolio_returns.std() * np.sqrt(252))

    st.subheader("Portfolio Metrics")
    st.write(f"**Total Return:** {total_return:.2%}")
    st.write(f"**SPY Benchmark Return:** {benchmark_return:.2%}")
    st.write(f"**Outperformance:** {outperformance:.2%}")
    st.write(f"**Annualized Volatility:** {volatility:.2%}")
    st.write(f"**Sharpe Ratio:** {sharpe:.2f}")

    # Portfolio vs SPY chart
    st.markdown('<div class="chart-box-yellow">', unsafe_allow_html=True)
    st.subheader("Portfolio vs SPY — Cumulative Returns")

    cum_df = pd.DataFrame({
        "Portfolio": (1 + portfolio_returns).cumprod(),
        "SPY": (1 + benchmark_returns).cumprod()
    })

    st.line_chart(cum_df)
    st.markdown("</div>", unsafe_allow_html=True)

except Exception as e:
    st.error("Portfolio error — check that you entered exactly 5 tickers.")
