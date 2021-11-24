from pandas.core.algorithms import mode
import streamlit as st
import pandas as pd 
import yfinance as yf 
import quantstats as qs
import plotly

qs.extend_pandas()


st.set_page_config(layout = "wide")






cryptos = ["BTC-USD", "ETH-USD", "BNB-USD", "XRP-USD", "ADA-USD"]
indexes = ["SPY", "QQQ"]
strategies = ["Stacked BTC", "Stacked BTC Fast", "Stacked ETH Hyper"]

options = strategies + cryptos + indexes
col1, col2, col3 = st.columns((1, 3, 1))
col2.title("Technical Analysis Dashboard")

ticker = col2.selectbox("Choose Ticker", options)
def get_data(ticker):
    
    if ticker[0:7] != "Stacked":
        print(ticker)
        ticker_data = yf.download(ticker, start="2016-01-01", end="2021-11-17")
        ticker_data = pd.DataFrame(ticker_data["Close"])
        ticker_data = ticker_data.rename(columns={"Close": ticker})
    else:
        strat = ticker
        strat = strat.replace(" ", "_")
        ticker_data = pd.read_csv(strat+".csv")
        ticker_data = ticker_data.set_index("datetime")
        ticker_data.index = [x[:10] for x in ticker_data.index]
        ticker_data.index = pd.to_datetime(ticker_data.index)
        ticker_data = pd.DataFrame(ticker_data["Strategy"])
        ticker_data = ticker_data.rename(columns={"Strategy": ticker})
        
    return ticker_data



######################## Format Ticker Data ##########################
ticker_data = get_data(ticker)
print(ticker_data)
ticker_qs = ticker_data.pct_change()


################################# Graph Ticker Data ##############################
col2.subheader(ticker +" Price Chart")
col2.line_chart(ticker_data, height = 500)




########################## Format Index Data ########################
# index_data = yf.download(indexes, start="2016-01-01", end="2021-11-17")
# index_options = options.copy()
# index_options.remove(ticker)
index_choice = col2.selectbox("Choose Benchmark", options, index = 3)

if index_choice == ticker:
    index_choice = "SPY"

index_choice_data = get_data(index_choice)
print(index_choice_data)
# index_choice_data = pd.DataFrame(index_data["Close"][index_choice])
index_qs = index_choice_data.pct_change()








ticker_qs = ticker_qs.dropna()
ticker_qs = ticker_qs.squeeze()

index_qs = index_qs.dropna()
index_qs = index_qs.squeeze()



######################## Graph Combined Data #########################

ticker_port = pd.DataFrame(qs.utils.make_portfolio(ticker_qs, start_balance = 100))
ticker_port.columns = [ticker]
index_port = pd.DataFrame(qs.utils.make_portfolio(index_qs, start_balance = 100))
index_port.columns = [index_choice]

combined_data = ticker_port.join(index_port, how = "outer")
combined_data = combined_data.dropna()

col2.subheader("Compare " + ticker + " to an benchmark")
col2.line_chart(combined_data, height = 500)

################## Rolling Sharpe ###########################
ticker_sharpe = pd.DataFrame(qs.stats.rolling_sharpe(ticker_qs, 0., 182, True, 365))
index_sharpe = pd.DataFrame(qs.stats.rolling_sharpe(index_qs, 0., 126, True, 252))

rolling_sharpe = ticker_sharpe.join(index_sharpe, how="outer")
rolling_sharpe = rolling_sharpe.dropna()

col2.subheader("Rolling Sharpe Ratios")
col2.line_chart(rolling_sharpe, height = 500)


################## Drawdown Chart ###########################
ticker_drawdown = pd.DataFrame(qs.stats.to_drawdown_series(ticker_qs))
index_drawdown = pd.DataFrame(qs.stats.to_drawdown_series(index_qs))

drawdown = ticker_drawdown.join(index_drawdown, how="outer")
drawdown = drawdown.dropna()

col2.subheader("Drawdown Chart")
col2.line_chart(drawdown, height = 500)

################## Volatility Chart ###########################
ticker_volatility = pd.DataFrame(qs.stats.rolling_volatility(ticker_qs, 182, 365))
index_volatility = pd.DataFrame(qs.stats.rolling_volatility(index_qs))

rolling_volatility = ticker_volatility.join(index_volatility, how="outer")
rolling_volatility = rolling_volatility.dropna()

col2.subheader("6 Month Rolling Volatility")
col2.line_chart(rolling_volatility, height = 500)



##################### Heatmap ##############################
fig = ticker_qs.plot_monthly_heatmap(show= False)
col2.subheader("Monthly Returns Heatmap for " + ticker)
col2.pyplot(fig, height = 500)



########################### Stats ####################################
metrics = qs.reports.metrics(ticker_qs, benchmark = index_qs, display = False)
bad_formatted = ["Risk-Free Rate ", "Time in Market ", "Cumulative Return ", "CAGR﹪", "Max Drawdown ", "MTD ", "3M ", "6M ", "YTD ", "1Y ", "3Y (ann.) ", "5Y (ann.) ", "10Y (ann.) ", "All-time (ann.) ", "Avg. Drawdown "]

for stat in bad_formatted:
    
    metrics.loc[stat]["Strategy"] = str(round(float(str(metrics.loc[stat]["Strategy"]).replace(",", ""))  * 100, 1)) + "%"
    metrics.loc[stat]["Benchmark"] = str(round(float(str(metrics.loc[stat]["Benchmark"]).replace(",", "")) * 100, 1)) + "%"

metrics.columns = [ticker, index_choice]

metrics_str = metrics.astype(str)
col2.dataframe(metrics_str, width = 700, height = 1200)