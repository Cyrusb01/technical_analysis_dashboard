from pandas.core.algorithms import mode
import streamlit as st
import pandas as pd 
import yfinance as yf 
import quantstats as qs
import plotly
from datetime import datetime

def get_data(ticker):
    
    if ticker[0:10] != "Blockforce":
        print(ticker)
        now = datetime.now()
        now_str = now.strftime('%Y-%m-%d')
        print(now_str)
        ticker_data = yf.download(ticker, start="2016-01-01", end=now_str)
        ticker_data = pd.DataFrame(ticker_data["Close"])
        ticker_data = ticker_data.rename(columns={"Close": ticker})
        new_ticker = ticker
    else:
        strat = ticker
        strat = strat.replace(" ", "_")
        ticker_data = pd.read_csv(strat+".csv")
        ticker_data = ticker_data.set_index("datetime")
        ticker_data.index = [x[:10] for x in ticker_data.index]
        ticker_data.index = pd.to_datetime(ticker_data.index)
        ticker_data = pd.DataFrame(ticker_data["Strategy"])
        new_ticker = ticker[:10] + ticker[25:]
        ticker_data = ticker_data.rename(columns={"Strategy": new_ticker})
        
    return [ticker_data, new_ticker]
qs.extend_pandas()


st.set_page_config(layout = "wide")






cryptos = ["BTC-USD", "ETH-USD", "BNB-USD", "XRP-USD", "ADA-USD", "SOL1-USD"]
indexes = ["SPY", "QQQ"]
strategies = ["Blockforce Alpha Predator BTC Daily", "Blockforce Alpha Predator BTC Fast", "Blockforce Alpha Predator ETH Hyper"]

options = strategies + cryptos + indexes
a, title, b = st.columns((1, 4, 1))
a, input1, input2, b = st.columns((1, 2, 2, 1))
col1, col2, col3 = st.columns((1, 5, 1))
a, fig1, fig2, b= st.columns((1, 3, 3, 1))
a, fig3, fig4, b= st.columns((1, 3, 3, 1))
a, stats, b = st.columns((1, 4, 1))


title.title("Quantitative Strategy and Asset Dashboard")

ticker = input1.selectbox("Choose Ticker", options)
index_choice = input2.selectbox("Choose Benchmark", options, index = 3)




######################## Format Ticker Data ##########################
ticker_data, ticker = get_data(ticker)
print(ticker_data)
ticker_qs = ticker_data.pct_change()
########################## Format Index Data ########################
if index_choice == ticker:
    index_choice = "SPY"

index_choice_data, index_choice = get_data(index_choice)
print(index_choice_data)
index_qs = index_choice_data.pct_change()



########################## Formatting Data ##############################
combined_data = pd.DataFrame(ticker_qs).join(pd.DataFrame(index_qs), how = "outer")
combined_data = combined_data.dropna()

ticker_qs = combined_data[ticker]
index_qs = combined_data[index_choice]



################################# Graph Ticker Data ##############################
# col2.subheader(ticker +" Price Chart")
# col2.line_chart(ticker_data, height = 500)

######################## Graph Combined Data #########################





ticker_port = pd.DataFrame(qs.utils.make_portfolio(ticker_qs, start_balance = 100))
ticker_port.columns = [ticker]
index_port = pd.DataFrame(qs.utils.make_portfolio(index_qs, start_balance = 100))
index_port.columns = [index_choice]

combined_data = ticker_port.join(index_port, how = "outer")
combined_data = combined_data.dropna()

col2.subheader("Compare " + ticker + " to an benchmark")
col2.line_chart(combined_data, width = 1150, height = 500, use_container_width = False)

################## Rolling Sharpe ###########################
ticker_sharpe = pd.DataFrame(qs.stats.rolling_sharpe(ticker_qs, 0., 182, True, 365))
index_sharpe = pd.DataFrame(qs.stats.rolling_sharpe(index_qs, 0., 126, True, 252))

rolling_sharpe = ticker_sharpe.join(index_sharpe, how="outer")
rolling_sharpe = rolling_sharpe.dropna()

fig1.subheader("Rolling Sharpe Ratios")
fig1.line_chart(rolling_sharpe, width = 600, height = 300, use_container_width = False)


################## Drawdown Chart ###########################
ticker_drawdown = pd.DataFrame(qs.stats.to_drawdown_series(ticker_qs))
index_drawdown = pd.DataFrame(qs.stats.to_drawdown_series(index_qs))

drawdown = ticker_drawdown.join(index_drawdown, how="outer")
drawdown = drawdown.dropna()

fig2.subheader("Drawdown Chart")
fig2.line_chart(drawdown, width = 600, height = 300, use_container_width = False)

################## Volatility Chart ###########################
ticker_volatility = pd.DataFrame(qs.stats.rolling_volatility(ticker_qs, 182, 365))
index_volatility = pd.DataFrame(qs.stats.rolling_volatility(index_qs))

rolling_volatility = ticker_volatility.join(index_volatility, how="outer")
rolling_volatility = rolling_volatility.dropna()

fig3.subheader("6 Month Rolling Volatility")
fig3.line_chart(rolling_volatility, width = 600, height = 300, use_container_width = False)






########################### Stats ####################################
metrics = qs.reports.metrics(ticker_qs, benchmark = index_qs, display = False)
bad_formatted = ["Risk-Free Rate ", "Time in Market ", "Cumulative Return ", "CAGR﹪", "Max Drawdown ", "MTD ", "3M ", "6M ", "YTD ", "1Y ", "3Y (ann.) ", "5Y (ann.) ", "10Y (ann.) ", "All-time (ann.) ", "Avg. Drawdown "]

for stat in bad_formatted:
    
    metrics.loc[stat]["Strategy"] = str(round(float(str(metrics.loc[stat]["Strategy"]).replace(",", ""))  * 100, 1)) + "%"
    metrics.loc[stat]["Benchmark"] = str(round(float(str(metrics.loc[stat]["Benchmark"]).replace(",", "")) * 100, 1)) + "%"

metrics.columns = [ticker, index_choice]



###################### Bar Chart ###################################
ticker_sortino = metrics.loc["Sortino"][ticker]
index_sortino = metrics.loc["Sortino"][index_choice]

df = pd.DataFrame(list(zip([ticker_sortino, 0], [0, index_sortino])),
               columns =[ticker, index_choice])


s = pd.Series([ticker, index_choice])
df = df.set_index(s)
fig4.subheader("Sortino Ratios")
fig4.bar_chart(df, width = 600, height = 410, use_container_width = False)

# df = pd.read_csv("https://github.com/eervin123/ember_strategy_upgrade/blob/42a473cde02b5499cbef708529d09100d66e3f3f/output/stacked/eth_hyper/stacked_eth_hyper_stats.csv#L1")

print(df)

# url="https://raw.githubusercontent.com/eervin123/backtesting-crypto/42a473cde02b5499cbef708529d09100d66e3f3f/output/stacked/eth_hyper/stacked_eth_hyper_stats.csv?token=ASTDTEMD26ICBKFVZV4EHCDBU2CGY"
# c=pd.read_csv(url)
# print(c)
# st.bar_chart(df)


##################### Heatmap ##############################
fig = ticker_qs.plot_monthly_heatmap(show= False)
stats.subheader("Monthly Returns Heatmap")
stats.pyplot(fig, width = 600, height = 300, use_container_width = False)




metrics_str = metrics.astype(str)
stats.dataframe(metrics_str, width = 700, height = 1200)