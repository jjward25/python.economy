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
# Set Streamlit to use the fill page width
st.set_page_config(layout="wide")
daily_health_score = 5
daily_health_df = pd.DataFrame()





###############################################################################
##### Indexes #####
###############################################################################
##! Define the ticker symbols
indexTickers = ['^DJI','^GSPC','^IXIC']
#indexNames = ['Dow Jones Industrial Average','S&P 500','NASDAQ Composite']

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
indexes_final = pd.merge(indexes_final,indexes_previous, on='Symbol',how='left')
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
        r['Daily Health Score'] = index_daily_score
    if r['Daily Change $'] > 0:
        index_daily_score = index_daily_score + .5
        r['Daily Health Score'] = index_daily_score

# Convert everything to dollar (string) format
indexes_final['Avg Close $'] = indexes_final['Avg Close $'].apply(lambda x: f"${x:,.2f}")
indexes_final['Max Price $'] = indexes_final['Max Price $'].apply(lambda x: f"${x:,.2f}")
indexes_final['Last Close $'] = indexes_final['Last Close $'].apply(lambda x: f"${x:,.2f}")
indexes_final['Previous Close $'] = indexes_final['Previous Close $'].apply(lambda x: f"${x:,.2f}")
indexes_final['Daily Change $'] = indexes_final['Daily Change $'].apply(lambda x: f"${x:,.2f}")
indexes_final['Daily Change %'] = indexes_final['Daily Change %'].apply(lambda x: f"{x:,.2f}%")
#print(indexes_final)

##! Health Prep
major_market_health = pd.DataFrame({'Metric':'Major Market Health Score','Score':index_daily_score},index=[0])
major_market_reference =  pd.DataFrame({'Score':[-1.5,-1,-.5,.5,1,1.5],
                          'Reason':['More Major Indexes lost value than gained value today (Markets).','More Major Indexes lost value than gained value today (Markets).','More Major Indexes lost value than gained value today (Markets).','More Major Indexes gained value than lost value today (Markets).','More Major Indexes gained value than lost value today (Markets).','More Major Indexes gained value than lost value today (Markets).'],
                          'Metric':['Major Market Health Score','Major Market Health Score','Major Market Health Score','Major Market Health Score','Major Market Health Score','Major Market Health Score']
                          })
major_market_health = pd.merge(major_market_health,major_market_reference, on=['Metric','Score'],how='left')

##! Health DF and Score Update
daily_health_df = pd.concat([daily_health_df,major_market_health],axis=0)
daily_health_score = sum(daily_health_df['Score'])
#print(daily_health_df)





##########################################################################################
##### Caps + Commodities #####
##########################################################################################
##! Define the ticker symbols
industryTickers = ['DFLVX','DFSVX','GC=F','CL=F','LBS=F']
#industryNames = ['Dow Jones Industrial Average','S&P 500','NASDAQ Composite']

##! Query the avg close and max price for the time period, and the last two closing prices for the tickers into DFs 
cap_avg = yf.download(tickers=industryTickers,period="day",start=start_date,end=end_date)['Close'].mean()
cap_avg = pd.DataFrame({'Symbol':cap_avg.index, 'Avg Close $':cap_avg.values})
cap_max = yf.download(tickers=industryTickers,period="day",start=start_date,end=end_date)['High'].max()
cap_max = pd.DataFrame({'Symbol':cap_max.index, 'Max Price $':cap_max.values})
cap_last = yf.download(tickers=industryTickers,period="1d")['Close'].iloc[0]
cap_last = pd.DataFrame({'Symbol':cap_last.index, 'Last Close $':cap_last.values})
cap_previous = yf.download(tickers=industryTickers,period="2d")['Close'].iloc[-2]
cap_previous = pd.DataFrame({'Symbol':cap_previous.index, 'Previous Close $':cap_previous.values})

##! Create the merged dataframe
cap_final = pd.merge(cap_avg,cap_max, on='Symbol',how='left') ## Merge Average and Max
cap_final = pd.merge(cap_final,cap_last, on='Symbol',how='left') ## Merge that with Last Close
cap_final = pd.merge(cap_final,cap_previous, on='Symbol',how='left')
##! Create Calculated Fields
cap_final['Daily Change $'] = cap_final['Last Close $'] - cap_final['Previous Close $']
cap_final['Daily Change %'] = (cap_final['Daily Change $']/cap_final['Previous Close $'])*100 
# print(cap_final)

# Health Score Variables
cap_variance = cap_final.loc[cap_final['Symbol'] == 'DFSVX', 'Daily Change $'].iloc[0] - cap_final.loc[cap_final['Symbol'] == 'DFLVX', 'Daily Change $'].iloc[0]
cap_health_score = 0
if cap_variance < 0:
        cap_health_score = cap_health_score-.5      
if cap_variance > 0:
    cap_health_score = cap_health_score+.5

gas_health_score = 0
if cap_final.loc[cap_final['Symbol'] == 'CL=F', 'Daily Change $'].iloc[0] > 0:
    gas_health_score = -.5
if cap_final.loc[cap_final['Symbol'] == 'CL=F', 'Daily Change $'].iloc[0] < 0:
    gas_health_score = .5
# Convert everything to dollar (string) format
cap_final['Avg Close $'] = cap_final['Avg Close $'].apply(lambda x: f"${x:,.2f}")
cap_final['Max Price $'] = cap_final['Max Price $'].apply(lambda x: f"${x:,.2f}")
cap_final['Last Close $'] = cap_final['Last Close $'].apply(lambda x: f"${x:,.2f}")
cap_final['Previous Close $'] = cap_final['Previous Close $'].apply(lambda x: f"${x:,.2f}")
cap_final['Daily Change $'] = cap_final['Daily Change $'].apply(lambda x: f"${x:,.2f}")
cap_final['Daily Change %'] = cap_final['Daily Change %'].apply(lambda x: f"{x:,.2f}%")
#print(cap_final)


##! Health Prep
cap_health = pd.DataFrame({'Metric':'Small Cap Health Score','Score':cap_health_score},index=[0])
cap_reference = pd.DataFrame({'Score':[-.5,0,.5],
                 "Reason":["Large Cap Outperformed Small Cap (Competiton).","Small and Large Cap Growth is equal (Competiton).","Small Cap Outperforming Large Cap (Competiton)."],
                 'Metric':['Small Cap Health Score','Small Cap Health Score','Small Cap Health Score']
                 })
cap_health = pd.merge(cap_health,cap_reference, on=['Metric','Score'],how='left')

gas_health = pd.DataFrame({'Metric':'Gas Health Score','Score':gas_health_score},index=[0])
gas_reference = pd.DataFrame({'Score':[-.5,.5],
                 "Reason":["Oil is up (Inflationary).","Oil is down (Deflationary)."],
                 'Metric':['Gas Health Score','Gas Health Score']
                 })
gas_health = pd.merge(gas_health,gas_reference, on=['Metric','Score'],how='left')

##! Health DF and Score Update
daily_health_df = pd.concat([daily_health_df,cap_health],axis=0)
daily_health_df = pd.concat([daily_health_df,gas_health],axis=0)
daily_health_score = sum(daily_health_df['Score'])
#print(daily_health_df)
#print(daily_health_score)

##########################################################################################
##########################################################################################
##### Output #####
##########################################################################################
##########################################################################################
market_health_df = daily_health_df.loc[np.isin(daily_health_df,['Major Market Health Score','Gas Health Score']).any(axis=1)]
competition_health_df = daily_health_df.loc[np.isin(daily_health_df,['Small Cap Health Score']).any(axis=1)]


##! Sidebar: Health Score and  Date input form (for trend charts)
with st.sidebar:
    st.write(f'# Daily Health Score: {daily_health_score}')
    st.write('### Trend Chart Date Range')
    st.write('Please enter dates in the format shown.')
    _input = st.text_input("Start Date: YYYY-MM-DD")
    _input2 = st.text_input("End Date: YYYY-MM-DD")
    if _input:
        start_date = _input
    if _input2:
        end_date = _input2        

##! Header
st.write(f'# Daily Health Score: {daily_health_score}')
st.divider()
col1, col2 = st.columns([1,1.3])
with col1:
    #st.area_chart(data=None, *, x=None, y=None, width=0, height=0, use_container_width=True)
    st.bar_chart(daily_health_df[['Score','Metric']], y='Score',x='Metric', height=250,width=500, use_container_width=False)
with col2:
    daily_health_df
st.divider()
##! Section Header
my_expander = st.expander(f"## Market Health: {sum(market_health_df['Score'])}", expanded=True)
with my_expander:
    ####################################
    ##! Major Markets Output:  
    ####################################
    st.write('## Major Markets')
    st.write('*Other factors to consider include the performance of key sectors  and overall market volatility.*')
    col1, col2 = st.columns([1.3,1])
    with col1:
        if index_daily_variance < 0:
            st.write(f""" The Dow Jones Industrial Average, S&P 500, and NASDAQ Composite lost ${index_daily_variance:,.2f} total in value today.""")
        if index_daily_variance > 0:
            st.write(f""" The Dow Jones Industrial Average, S&P 500, and NASDAQ Composite gained ${index_daily_variance:,.2f} total in value today.""")
        # Scorecard summary: Rewrite this section as scorecard df (score, text) and write the text based on the score
        if index_daily_score == -1.5:
            st.write(f""" The Dow Jones Industrial Average, S&P 500, and NASDAQ Composite all lost value yesterday for a *{index_daily_score}* Daily Health Score.""")
            st.write('')
        if index_daily_score == -1:
            st.write(f""" 2 major markets lost value yesterday for a *{index_daily_score}* Daily Health Score.""")
            st.write('')
        if index_daily_score == -.5:
            st.write(f""" More major markets lost than gained yesterday for a *{index_daily_score}* Daily Health Score.""")
            st.write('')
        if index_daily_score == 0:
            st.write(f""" Market Holiday - no major indexes gained or lost yesterday for a *{index_daily_score}* Daily Health Score.""")
            st.write('')
        if index_daily_score == .5:
            st.write(f""" More major markets gained than lost yesterday for a *{index_daily_score}* Daily Health Score.""")
            st.write('')
        if index_daily_score == 1:
            st.write(f""" 2 major markets gained value yesterday for a *{index_daily_score}* Daily Health Score.""")
            st.write('')
        if index_daily_score == 1.5:
            st.write(f""" The Dow Jones Industrial Average, S&P 500, and NASDAQ Composite all gained value yesterday for a *{index_daily_score}* Daily Health Score.""")
            st.write('')
    # The merged dataframe and a line chart of closing prices for the selected time period
        indexes_final
    with col2:
        index_chart = yf.download("^DJI ^GSPC ^IXIC", start=start_date, end=end_date, period='1d')
        st.line_chart(index_chart.Close)
    st.write(""" *Data pulled from Yahoo Finance* """)

##! Section Header
my_expander = st.expander(f"## Competition: {sum(competition_health_df['Score'])}", expanded=False)
with my_expander:
    ####################################
    ##! Cap + Commodities Column Output:
    #################################### 
    st.write('## Small Cap Value vs. Large Cap Growth')
    col1, col2 = st.columns([1.3,1])
    with col1:
        if cap_variance < 0:
            st.write(f""" The Large Cap stocks outperformed Small Cap value stocks for a *{cap_health_score}* Daily Health Score.""")
        if cap_variance > 0:
            st.write(f""" The Small Cap value stocks outperformed Large Cap stocks for a *{cap_health_score}* Daily Health Score.""")
        if gas_health_score < 0:
            st.write(f""" The price of Gas rose for a *{gas_health_score}* Daily Health Score.""")
            st.write('')
        if gas_health_score > 0:
            st.write(f""" The price of Gas fell for a *{gas_health_score}* Daily Health Score.""")
            st.write('')
        cap_final
    with col2:
        index_chart = yf.download("DFLVX DFSVX GC=F CL=F LBS=F", start=start_date, end=end_date, period='1d')
        st.write(""" Caps + Commodities Performance """)
        st.line_chart(index_chart.Close)
    st.write(""" *Data pulled from Yahoo Finance* """)


#https://www.dol.gov/agencies/odep/research-evaluation/EPRmap.json
