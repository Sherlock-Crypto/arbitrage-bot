import streamlit as st
import psycopg2
import pandas as pd
import datetime
import plotly.express as px
import warnings
from config import *


warnings.filterwarnings('ignore')
st.set_page_config(page_title='SHERLOCK CRYPTO - Analytics',  layout='wide', page_icon=':bar_chart:')


# Uses st.experimental_singleton to only run once.
@st.experimental_singleton
def init_connection():
    return psycopg2.connect(st.secrets["postgres"], sslmode='require')

# Uses st.experimental_memo to only rerun when the query changes or after 10 min.
@st.experimental_memo(ttl=600)
def create_table():
    return pd.read_sql_query("SELECT * from events;", conn)


@st.experimental_memo(ttl=600)
def best_pairs():
    fig = px.bar(profit_sum_pair, y='pair', x='profit', color='pair',
                 width=600, height=900,
                 labels={'profit': 'Total profit (%)', 'pair':'Token pair'}
                 )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig)

@st.experimental_memo(ttl=600)
def historical_profit_by_pair():
    fig_top = px.line(top, x='timestamp', y='profit', color='pair',
                      title='TOP pairs profit on each iteration:',
                      width=600, height=400,
                      labels={'profit': 'Profit (%)'}
                      )
    fig_low = px.line(low, x='timestamp', y='profit', color='pair',
                      title='LOW pairs profit on each iteration:',
                      width=600, height=400,
                      labels={'profit': 'Profit (%)'}
                      )
    st.plotly_chart(fig_top)
    st.plotly_chart(fig_low)


@st.experimental_memo(ttl=600)
def events_count():
    fig = px.histogram(df, y='pair', color='pair',
                       width=600, height=900,
                       labels={'pair':'Token pair'})\
        .update_xaxes(categoryorder='total descending')
    fig.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
    st.plotly_chart(fig)


@st.experimental_memo(ttl=600)
def buy_exc():
    fig = px.histogram(df, x='buy_at', color='buy_at',
                       title='Buy events count, by exchange:',
                       width=600, height=500,
                       labels={'buy_at': 'BUY exchange'})
    fig.update_layout(xaxis={'categoryorder': 'total descending'}, showlegend=False)
    st.plotly_chart(fig)


@st.experimental_memo(ttl=600)
def sell_exc():
    fig = px.histogram(df, x='sell_at', color='sell_at',
                       title='Sell events count, by exchange:',
                       width=600, height=500,
                       labels={'sell_at': 'SELL exchange'})
    fig.update_layout(xaxis={'categoryorder': 'total descending'}, showlegend=False)
    st.plotly_chart(fig)


@st.experimental_memo(ttl=600)
def cumsum():
    fig_top = px.line(top, x='timestamp', y='cumsum_profit', color='pair',
                      title='Cumulative profit of TOP pairs:',
                      width=600, height=400,
                      labels={'cumsum_profit': 'Cumulative profit (%)'}
                      )
    fig_low = px.line(low, x='timestamp', y='cumsum_profit', color='pair',
                      title='Cumulative profit of LOW pairs:',
                      width=600, height=400,
                      labels={'cumsum_profit': 'Cumulative profit (%)'}
                      )
    st.plotly_chart(fig_top)
    st.plotly_chart(fig_low)


conn = init_connection()
df = create_table()

current_time = df.timestamp.max()
previous_time = df.timestamp.unique()[-2]
previous_event_count = df[df.timestamp==previous_time].shape[0]

df['cumsum_profit'] = df.groupby('pair')['profit'].cumsum()
profit_sum_pair = df.copy()
profit_sum_pair = profit_sum_pair.groupby('pair').agg({'profit': 'sum'}) \
        .sort_values('profit', ascending=False) \
        .reset_index()
profit_mean_pair = df.groupby('pair').agg({'profit':'mean'}).reset_index()

divider = profit_mean_pair['profit'].mean()
top_pairs = profit_mean_pair[profit_mean_pair.profit >= divider]['pair']
low_pairs = profit_mean_pair[profit_mean_pair.profit < divider]['pair']
top = df[df.pair.isin(top_pairs)]
low = df[df.pair.isin(low_pairs)]


st.title('Crypto arbitrage analytics')
st.markdown('This is an analytical dashboard based on crypto arbitrage events dataset that is being constantly updated by **Sherlock Crypto**.')
st.markdown('If you want to get around 20 profitable arbitrage orders every 30 minutes, consider subscribing to our [**Sherlock Crypto Bot**](https://t.me/ArbitrageScannerBot)')

m1, m2 = st.columns((1, 1))
t1, t2 = st.columns((1, 1))

overall_events = df.shape[0]
m1.metric('Overall events detected', overall_events)

last_events_count = df[df.timestamp == current_time].shape[0]
m2.metric('Events on last refresh', last_events_count,
          delta = str(last_events_count-previous_event_count)+' compared to previous')

t1.metric('Last refreshed', current_time.strftime('%H:%M'))

next_refresh = datetime.timedelta(seconds=PARSE_INTERVAL+60)
estimated_time = current_time + next_refresh
t2.metric('Next refresh estimated time', estimated_time.strftime('%H:%M'))

st.subheader('Arbitrage profit on each iteration, by pair:')
historical_profit_by_pair()

st.subheader('Total arbitrage profit, by pair:')
best_pairs()

st.subheader('Arbitrage events count, by pair:')
events_count()

st.subheader('Buy/sell exchanges count:')
buy_exc()
sell_exc()

st.subheader('Cumulative profit, by pair:')
st.caption('Pairs are divided into TOP and LOW by their profitability')
cumsum()