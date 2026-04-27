import streamlit as st
import yfinance as yf
from yfinance import pdr_override
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

pdr_override()
st.set_page_config(page_title="Final Project Dashboard", layout="wide")


# -----------------------------------------------------------
# SAFE DOWNLOADER FOR STREAMLIT CLOUD
# -----------------------------------------------------------
def safe_download(ticker, period="6mo", interval="1d"):
    try:
        df = yf.download(
            ticker,
            period=period,
            interval=interval,
            progress=False,
            threads=False
        )
        if df is None or df.empty:
            return None
        return df
    except Exception:
        return None


# -----------------------------------------------------------
# EMOJI + COLOR HELPERS
# -----------------------------------------------------------
def trend_emoji(x):
    if x == "Strong Uptrend":
        return "🟢📈 Strong Uptrend"
    elif x == "Strong Downtrend":
        return "🔴📉 Strong Downtrend"
    else:
        return "🟡〰️ Mixed Trend"


def rsi_emoji(x):
    if "Overbought" in x:
        return "🔴🔥 Overbought (Sell Signal)"
    elif "Oversold" in x:
        return "🟢💎 Oversold (Buy Signal)"
    else:
        return "🟡 Neutral"


def vol_emoji(level):
    if level == "High":
        return "🔴 High Volatility"
    elif level == "Medium":
        return "🟡 Medium Volatility"
    else:
        return "🟢 Low Volatility"


# -----------------------------------------------------------
# CSS — Green & Yellow Chart Borders
# -----------------------------------------------------------
st.markdown("""
<style>
.chart-box-green {
    border: 5px solid #00cc44;
    padding: 12px;
    border-radius: 12px;
    margin-bottom: 25px;
}
.chart-box-yellow {
    border: 5px solid #ffeb3b;
    padding: 12px;
    border-radius: 12px;
    margin-bottom: 25px;
}
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------
# SIDEBAR — INPUTS + REAL-TIME VALIDATION
# -----------------------------------------------------------
st.sidebar.title("Input Settings")

stock = st.sidebar.text_input("Stock Ticker:", "AAPL").upper()

portfolio_raw = st.sidebar.text_input(
    "Portfolio (Enter 5 tickers):",
    "AAPL MSFT AMZN GOOG NVDA"
)
portfolio = portfolio_raw.upper().split()

# Real-time validation
invalid_tickers = []
for t in [stock] + portfolio:
    if not t.isalpha() or len(t) > 6:
        invalid_tickers.append(t)

if invalid_tickers:
    st.sidebar.error(f"Invalid tickers detected: {', '.join(invalid_tickers)}")


# -----------------------------------------------------------
# MAIN HEADER
# -----------------------------------------------------------
st.title("📊 Final Project Financial Dashboard")

# -----------------------------------------------------------
# PART 1 — INDIVIDUAL STOCK ANALYSIS
# -----------------------------------------------------------
st.header("Part 1: Individual Stock Analysis")

data = safe_download(stock)

if data is None:
    st.error("❌ Unable to retrieve stock data. Try another ticker.")
else:
    data["20MA"] = data["Close"].rolling(20).mean()
    data["50MA"] = data["Close"].rolling(50).mean()

    # Trend logic
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

    # Display results
    st.subheader(f"Results for {stock}")

    st.write(f"**Trend:** {trend_emoji(trend)}")
    st.write(f"**RSI:** {rsi_emoji(rsi_sig)} — {rsi_val:.2f}")
    st.write(f"**Volatility:** {vol_emoji(vol_class)} — {vol_val:.2%}")

    # Chart
    st.markdown('<div class="chart-box-green">', unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(10,4))
    ax.plot(data["Close"], label="Close", color="white")
    ax.plot(data["20MA"], label="20MA", color="cyan")
    ax.plot(data["50MA"], label="50MA", color="magenta")
    ax.legend()
    st.pyplot(fig)
    st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------------------------------------
# PART 2 — PORTFOLIO PERFORMANCE
# -----------------------------------------------------------
st.header("Part 2: Portfolio Performance Dashboard")

if len(portfolio) != 5:
    st.error("❌ Please enter exactly 5 tickers for the portfolio.")
else:
    prices = yf.download(portfolio, period="1y", progress=False)

    if prices is None or prices.empty:
        st.error("❌ Unable to load portfolio data.")
    else:
        prices = prices["Adj Close"]
        bench = safe_download("SPY", period="1y")

        if bench is None:
            st.error("❌ SPY benchmark could not be downloaded.")
        else:
            bench = bench["Adj Close"]

            returns = prices.pct_change().dropna()
            weights = np.array([1/5] * 5)
            portfolio_returns = (returns * weights).sum(axis=1)

            benchmark_returns = bench.pct_change().dropna()

            # Performance metrics
            total_return = (1 + portfolio_returns).prod() - 1
            bench_return = (1 + benchmark_returns).prod() - 1
            outperf = total_return - bench_return

            vol = portfolio_returns.std() * np.sqrt(252)
            sharpe = (portfolio_returns.mean()*252) / (portfolio_returns.std()*np.sqrt(252))

            st.subheader("Portfolio Metrics")

            st.write(f"**Total Return:** 🟦 {total_return:.2%}")
            st.write(f"**SPY Return:** 🟧 {bench_return:.2%}")
            st.write(f"**Outperformance:** {'🟢+' if outperf>0 else '🔴'} {outperf:.2%}")
            st.write(f"**Volatility:** {vol_emoji('High' if vol>0.4 else 'Medium' if vol>=0.25 else 'Low')} — {vol:.2%}")
            st.write(f"**Sharpe Ratio:** ⭐ {sharpe:.2f}")

            # Chart
            st.markdown('<div class="chart-box-yellow">', unsafe_allow_html=True)
            cumulative = pd.DataFrame({
                "Portfolio": (1 + portfolio_returns).cumprod(),
                "SPY": (1 + benchmark_returns).cumprod()
            })
            st.line_chart(cumulative)
            st.markdown("</div>", unsafe_allow_html=True)
