import streamlit as st
import pandas as pd 
import yfinance as yf 
import quantstats as qs
import plotly

qs.extend_pandas()


st.title("Technical Analysis Dashboard")
options = ["BTC-USD", "ETH-USD", "BNB-USD", "XRP-USD", "ADA-USD"]
ticker = st.selectbox("Choose Ticker", options)


# ticker = "BTC-USD"


ticker_data = yf.download(ticker, start="2016-01-01", end="2021-11-17")

ticker_data = pd.DataFrame(ticker_data["Close"])
ticker_data = ticker_data.rename(columns={"Close": ticker})
ticker_qs = ticker_data.pct_change()

st.subheader(ticker +" Price Chart")
st.line_chart(ticker_data)



st.subheader("Compare " + ticker + " to an benchmark")
indexes = ["SPY", "QQQ"]

index_data = yf.download(indexes, start="2016-01-01", end="2021-11-17")


index_choice = st.selectbox("Choose Ticker", indexes)
# index_choice = "SPY"


index_choice_data = pd.DataFrame(index_data["Close"][index_choice])

index_qs = index_choice_data.pct_change()

data = ticker_data.join(index_choice_data, how = "outer")


data = data.dropna()
# print(data_new)


# print("Average Return ", ticker_qs.avg_return())
st.line_chart(data)




# def to_plotly(fig):
    
#         fig = plotly.tools.mpl_to_plotly(fig)
#         return plotly.plotly.iplot(fig, filename='quantstats-plot',
#                                    overwrite=True)



ticker_qs = ticker_qs.dropna()
ticker_qs = ticker_qs.squeeze()


index_qs = index_qs.dropna()
index_qs = index_qs.squeeze()


# print(ticker_qs)



################## Rolling Sharpe ###########################
ticker_sharpe = pd.DataFrame(qs.stats.rolling_sharpe(ticker_qs, 0., 182, True, 365))
index_sharpe = pd.DataFrame(qs.stats.rolling_sharpe(index_qs, 0., 126, True, 252))

rolling_sharpe = ticker_sharpe.join(index_sharpe, how="outer")
rolling_sharpe = rolling_sharpe.dropna()

st.subheader("Rolling Sharpe Ratios")
st.line_chart(rolling_sharpe)



################## Drawdown Chart ###########################
ticker_drawdown = pd.DataFrame(qs.stats.to_drawdown_series(ticker_qs))
index_drawdown = pd.DataFrame(qs.stats.to_drawdown_series(index_qs))

drawdown = ticker_drawdown.join(index_drawdown, how="outer")
drawdown = drawdown.dropna()

st.subheader("Drawdown Chart")
st.line_chart(drawdown)

################## Drawdown Chart ###########################
ticker_volatility = pd.DataFrame(qs.stats.rolling_volatility(ticker_qs, 182, 365))
index_volatility = pd.DataFrame(qs.stats.rolling_volatility(index_qs))

rolling_volatility = ticker_volatility.join(index_volatility, how="outer")
rolling_volatility = rolling_volatility.dropna()

st.subheader("6 Month Rolling Volatility")
st.line_chart(rolling_volatility)



# fig1 = ticker_qs.plot_rolling_volatility(show = False)
# st.pyplot(fig1)
fig = ticker_qs.plot_monthly_heatmap(show= False)
st.subheader("Monthly Returns Heatmap for " + ticker)
st.pyplot(fig)