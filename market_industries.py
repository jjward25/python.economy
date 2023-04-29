# Imports
import yfinance as yf
import streamlit as st
from datetime import date, timedelta
import pandas as pd
import numpy as np
# Date Variables
today = date.today()
start_date = today - timedelta(days=365)
end_date = today

##! Header
st.write("""
# JWEI
Joe Ward Economic Index
""")

## Date input form (to change date variables)
_input = st.text_input("Start Date: YYYY-MM-DD")
_input2 = st.text_input("End Date: YYYY-MM-DD")
if _input:
    start_date = _input
if _input2:
    end_date = _input2
else:
    st.write('Please enter dates in the format shown.')

##### Indexes #####
##! Define the ticker symbols
indexTickers = ['^DJI','^GSPC','^IXIC']
indexNames = ['Dow Jones Industrial Average','S&P 500','NASDAQ Composite']

##! Query the avg close and max price for the time period, and the last two closing prices for the tickers into DFs 
indexes_avg = yf.download(tickers=indexTickers,period="day",start=start_date,end=end_date)['Close'].mean()
indexes_avg = pd.DataFrame({'Symbol':indexes_avg.index, 'Avg Close $':indexes_avg.values})
indexes_max = yf.download(tickers=indexTickers,period="day",start=start_date,end=end_date)['High'].max()
indexes_max = pd.DataFrame({'Symbol':indexes_max.index, 'Max Price $':indexes_max.values})
indexes_last = yf.download(tickers=indexTickers,period="1d")['Close'].iloc[0]
indexes_last = pd.DataFrame({'Symbol':indexes_last.index, 'Last Close $':indexes_last.values})
indexes_previous = yf.download(tickers=indexTickers,period="2d")['Close'].iloc[-2]
indexes_previous = pd.DataFrame({'Symbol':indexes_previous.index, 'Previous Close $':indexes_previous.values})

##! Create the merged dataframe
indexes_final = pd.merge(indexes_avg,indexes_max, on='Symbol',how='left') ## Merge Average and Max
indexes_final = pd.merge(indexes_final,indexes_last, on='Symbol',how='left') ## Merge that with Last Close
indexes_final = pd.merge(indexes_final,indexes_previous, on='Symbol',how='left').rename(columns={'Avg Close $':'Avg Close $','High':'Max Price $','Last Close $ ':'Last Close $','Previous Close $':'Previous Close $'})

##! Create Calculated Fields
indexes_final['Daily Change $'] = indexes_final['Last Close $'] - indexes_final['Previous Close $']
indexes_final['Daily Change %'] = (indexes_final['Daily Change $']/indexes_final['Previous Close $'])*100 
# print(indexes_final)

# Health Score Variables
index_daily_variance = sum(indexes_final['Daily Change $'])
index_daily_score = 0
# Calc the health score
for i,r in indexes_final.iterrows():
    if r['Daily Change $'] < 0:
        index_daily_score = index_daily_score - .5
    if r['Daily Change $'] > 0:
        index_daily_score = index_daily_score + .5

# Convert everything to dollar format
indexes_final['Avg Close $'] = indexes_final['Avg Close $'].apply(lambda x: f"${x:,.2f}")
indexes_final['Max Price $'] = indexes_final['Max Price $'].apply(lambda x: f"${x:,.2f}")
indexes_final['Last Close $'] = indexes_final['Last Close $'].apply(lambda x: f"${x:,.2f}")
indexes_final['Previous Close $'] = indexes_final['Previous Close $'].apply(lambda x: f"${x:,.2f}")
indexes_final['Daily Change $'] = indexes_final['Daily Change $'].apply(lambda x: f"${x:,.2f}")
indexes_final['Daily Change %'] = indexes_final['Daily Change %'].apply(lambda x: f"{x:,.2f}%")
print(indexes_final)

##! Output: The merged dataframe and a line chart of closing prices for the selected time period
indexes_final
index_chart = yf.download("^DJI ^GSPC ^IXIC", start=start_date, end=end_date, period='1d')
st.write(""" Core Index Performance """)
st.line_chart(index_chart.Close)

if index_daily_variance < 0:
    st.write(f""" The Dow Jones Industrial Average, S&P 500, and NASDAQ Composite lost ${index_daily_variance:,.2f} total in value today.""")
if index_daily_variance > 0:
    st.write(f""" The Dow Jones Industrial Average, S&P 500, and NASDAQ Composite gained ${index_daily_variance:,.2f} total in value today.""")

## Rewrite as scorecard df (score, text) and write the text based on the score
if index_daily_score == -1.5:
    st.write(f""" The Dow Jones Industrial Average, S&P 500, and NASDAQ Composite all lost value yesterday for a *{index_daily_score}* Daily Health Score in the JWI Economic Indicator.""")
if index_daily_score == -1:
    st.write(f""" 2 major markets lost value yesterday for a *{index_daily_score}* Daily Health Score in the JWI Economic Indicator.""")
if index_daily_score == -.5:
    st.write(f""" More major markets lost than gained yesterday for a *{index_daily_score}* Daily Health Score in the JWI Economic Indicator.""")
if index_daily_score == 0:
    st.write(f""" Market Holiday - no major indexes gained or lost yesterday for a *{index_daily_score}* Daily Health Score in the JWI Economic Indicator.""")
if index_daily_score == .5:
    st.write(f""" More major markets gained than lost yesterday for a *{index_daily_score}* Daily Health Score in the JWI Economic Indicator.""")
if index_daily_score == 1:
    st.write(f""" 2 major markets gained value yesterday for a *{index_daily_score}* Daily Health Score in the JWI Economic Indicator.""")
if index_daily_score == 1.5:
    st.write(f""" The Dow Jones Industrial Average, S&P 500, and NASDAQ Composite all gained value yesterday for a *{index_daily_score}* Daily Health Score in the JWI Economic Indicator.""")
st.write(""" *Data pulled from Yahoo Finance* """)

##### Industries #####
industries = pd.DataFrame()
