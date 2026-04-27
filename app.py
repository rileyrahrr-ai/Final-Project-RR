{
  "nbformat": 4,
  "nbformat_minor": 0,
  "metadata": {
    "colab": {
      "provenance": []
    },
    "kernelspec": {
      "name": "python3",
      "display_name": "Python 3"
    },
    "language_info": {
      "name": "python"
    }
  },
  "cells": [
    {
      "cell_type": "markdown",
      "source": [
        "Part 1: Individual Stock Analysis\n",
        "\n",
        "Step 1: Data Collection\n",
        "• Download 6 months of daily stock data using yfinance\n",
        "• Use the closing price for analysis\n",
        "\n",
        "Step 2: Trend Analysis\n",
        "• Calculate current price\n",
        "• Calculate 20-day moving average\n",
        "• Calculate 50-day moving average\n",
        "• Strong Uptrend: Price > 20MA > 50MA\n",
        "• Strong Downtrend: Price < 20MA < 50MA\n",
        "• Mixed Trend: Otherwise\n",
        "\n",
        "Step 3: Momentum (RSI)\n",
        "• Calculate 14-day RSI\n",
        "• RSI > 70 → Overbought (Possible Sell Signal)\n",
        "• RSI < 30 → Oversold (Possible Buy Signal)\n",
        "• Otherwise → Neutral\n",
        "\n",
        "Step 4: Volatility\n",
        "• Calculate 20-day annualized volatility\n",
        "• High: > 40%\n",
        "• Medium: 25%–40%\n",
        "• Low: < 25%\n",
        "\n",
        "Step 5: Trading Recommendation\n",
        "Provide a final recommendation: Buy, Sell, or Hold, with a brief explanation.\n",
        "\n",
        "Part 2: Portfolio Performance Dashboard\n",
        "\n",
        "Step 1: Portfolio Setup\n",
        "• Select 5 stocks\n",
        "• Assign weights that sum to 1.00\n",
        "\n",
        "Step 2: Benchmark\n",
        "Use an ETF such as SPY as the benchmark.\n",
        "\n",
        "Step 3: Data Collection\n",
        "Download 1 year of historical price data.\n",
        "\n",
        "Step 4: Return Calculations\n",
        "• Calculate returns for each stock\n",
        "• Calculate portfolio returns\n",
        "• Calculate benchmark returns\n",
        "\n",
        "Step 5: Performance Metrics\n",
        "• Total return\n",
        "• Benchmark return\n",
        "• Outperformance / underperformance\n",
        "• Annualized volatility\n",
        "• Sharpe ratio\n",
        "\n",
        "Step 6: Interpretation\n",
        "• Did the portfolio outperform the benchmark?\n",
        "• Was it more or less risky?\n",
        "• Was it efficient based on Sharpe ratio?"
      ],
      "metadata": {
        "id": "jqSeWjYk6ioQ"
      }
    },
    {
      "cell_type": "code",
      "source": [
        "import streamlit as st\n",
        "import yfinance as yf\n",
        "import pandas as pd\n",
        "import matplotlib.pyplot as plt\n",
        "\n",
        "st.set_page_config(page_title = \"Stock Data Extraction App\",layout=\"wide\")\n",
        "\n",
        "st.title(\"Stock Data Extraction App\")\n",
        "\n",
        "st.write(\"Extract stock market prices from Yahoo Finance using a ticker symbol.\")\n",
        "\n",
        "st.sidebar.header(\"User Input\")\n",
        "\n",
        "ticker = st.sidebar.text_input(\"Enter Stock Ticker\", \"AAPL\")\n",
        "\n",
        "start_date = st.sidebar.date_input(\"Start Date\", pd.to_datetime(\"2023-01-01\"))\n",
        "\n",
        "end_date = st.sidebar.date_input(\"End Date\", pd.to_datetime(\"today\"))\n",
        "\n",
        "# Download the data\n",
        "if st.sidebar.button(\"Get Data\"):\n",
        "\n",
        "  # Create Ticker Object\n",
        "  stock = yf.Ticker(ticker)\n",
        "\n",
        "  # Download historical price data\n",
        "  df = stock.history(start=start_date, end=end_date)\n",
        "\n",
        "  # Check the data\n",
        "  if df.empty:\n",
        "    st.error(\"No data found. Please check the ticker symbol or date range.\")\n",
        "  else:\n",
        "      # Show success message\n",
        "      st.success(f\"Data successfully extracted for {ticker}\")\n",
        "\n",
        "      # Display company information\n",
        "      st.subheader(\"Company Information\")\n",
        "      info = stock.info\n",
        "\n",
        "      company_name = info.get(\"longName\", \"N/A\")\n",
        "      sector = info.get(\"sector\", \"N/A\")\n",
        "      industry = info.get(\"industry\", \"N/A\")\n",
        "      market_cap = info.get(\"marketCap\", \"N/A\")\n",
        "      website = info.get(\"website\", \"N/A\")\n",
        "\n",
        "      st.write(f\"**Company Name:** {company_name}\")\n",
        "      st.write(f\"**Sector:** {sector}\")\n",
        "      st.write(f\"**Industry:** {industry}\")\n",
        "      st.write(f\"**Market Cap:** {market_cap}\")\n",
        "      st.write(f\"**Website:** {website}\")\n",
        "\n",
        "      # Display stock data\n",
        "      st.subheader(\"Historical Stock Data\")\n",
        "      st.dataframe(df)\n",
        "\n",
        "      # Plot closing price\n",
        "      st.subheader(\"Closing Price Chart\")\n",
        "      fig, ax = plt.subplots()\n",
        "      ax.plot(df.index, df[\"Close\"])\n",
        "      ax.set_xlabel(\"Date\")\n",
        "      ax.set_ylabel(\"Closing Price\")\n",
        "      ax.set_title(f\"{ticker} Closing Price\")\n",
        "      st.pyplot(fig)\n",
        "\n",
        "      # Convert dataframe to CSV for download\n",
        "      csv = df.to_csv().encode(\"utf-8\")\n",
        "\n",
        "      # Download button for CSV\n",
        "      st.download_button(\n",
        "          label=\"Download Data as CSV\",\n",
        "          data=csv,\n",
        "          file_name=f\"{ticker}_stock_data.csv\",\n",
        "          mime=\"text/csv\"\n",
        "      )"
      ],
      "metadata": {
        "id": "yxep06V26kd_",
        "colab": {
          "base_uri": "https://localhost:8080/",
          "height": 384
        },
        "outputId": "0befab8d-82e8-4f0c-8e74-de0982815a32"
      },
      "execution_count": 1,
      "outputs": [
        {
          "output_type": "error",
          "ename": "ModuleNotFoundError",
          "evalue": "No module named 'streamlit'",
          "traceback": [
            "\u001b[0;31m---------------------------------------------------------------------------\u001b[0m",
            "\u001b[0;31mModuleNotFoundError\u001b[0m                       Traceback (most recent call last)",
            "\u001b[0;32m/tmp/ipykernel_3492/2320152680.py\u001b[0m in \u001b[0;36m<cell line: 0>\u001b[0;34m()\u001b[0m\n\u001b[0;32m----> 1\u001b[0;31m \u001b[0;32mimport\u001b[0m \u001b[0mstreamlit\u001b[0m \u001b[0;32mas\u001b[0m \u001b[0mst\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0m\u001b[1;32m      2\u001b[0m \u001b[0;32mimport\u001b[0m \u001b[0myfinance\u001b[0m \u001b[0;32mas\u001b[0m \u001b[0myf\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m      3\u001b[0m \u001b[0;32mimport\u001b[0m \u001b[0mpandas\u001b[0m \u001b[0;32mas\u001b[0m \u001b[0mpd\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m      4\u001b[0m \u001b[0;32mimport\u001b[0m \u001b[0mmatplotlib\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0mpyplot\u001b[0m \u001b[0;32mas\u001b[0m \u001b[0mplt\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m      5\u001b[0m \u001b[0;34m\u001b[0m\u001b[0m\n",
            "\u001b[0;31mModuleNotFoundError\u001b[0m: No module named 'streamlit'",
            "",
            "\u001b[0;31m---------------------------------------------------------------------------\u001b[0;32m\nNOTE: If your import is failing due to a missing package, you can\nmanually install dependencies using either !pip or !apt.\n\nTo view examples of installing some common dependencies, click the\n\"Open Examples\" button below.\n\u001b[0;31m---------------------------------------------------------------------------\u001b[0m\n"
          ],
          "errorDetails": {
            "actions": [
              {
                "action": "open_url",
                "actionText": "Open Examples",
                "url": "/notebooks/snippets/importing_libraries.ipynb"
              }
            ]
          }
        }
      ]
    }
  ]
}
