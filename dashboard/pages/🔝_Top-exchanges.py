import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px
import warnings

warnings.filterwarnings('ignore')
st.set_page_config(page_title='SHERLOCK CRYPTO - Top exchanges',  layout='wide', page_icon=':top:')


# Uses st.experimental_singleton to only run once.
@st.experimental_singleton
def init_connection():
    return psycopg2.connect(st.secrets["postgres"], sslmode='require')

# Uses st.experimental_memo to only rerun when the query changes or after 10 min.
@st.experimental_memo(ttl=600)
def create_table():
    return pd.read_sql_query("SELECT * from events;", conn)


@st.experimental_memo(ttl=600)
def best_exchanges_and_pairs():
    df_best_exc = df.copy()
    df_best_exc = df[df.timestamp == current_time]
    best_exc_pairs = dict()
    for _, row in df_best_exc.iterrows():
        exc_pair = row['sell_at'], row['buy_at']
        token_pair = {row['pair']:row['profit']}
        if exc_pair in best_exc_pairs.keys():
            best_exc_pairs[exc_pair]['count'] += 1
            best_exc_pairs[exc_pair]['token_pair'].update(token_pair)
        else:
            best_exc_pairs[exc_pair] = {'count':1, 'token_pair':token_pair}
    
    best_exc_pairs = sorted(best_exc_pairs.items(), key=lambda x: x[1]['count'], reverse=True)

    for num, exc in enumerate(best_exc_pairs, start=1):
        st.markdown(f"**{num}. {' - '.join(exc[0]).upper()}**")
        pair_profit = dict(sorted(exc[1]['token_pair'].items(), key=lambda x:x[1], reverse=True))
        df_pair_profit = pd.DataFrame.from_dict(pair_profit, orient='index').reset_index()
        df_pair_profit.columns = ['Pair', 'Profit']
        fig = px.bar(df_pair_profit, x='Pair', y='Profit')
        st.plotly_chart(fig)


if st.button('MANUAL REFRESH'):
    st.experimental_rerun()

conn = init_connection()
df = create_table()

current_time = df.timestamp.max()

st.header(f'Top exchanges [{current_time}]')
st.markdown('On this page you can find top exchanges and their best pairs with profits. The exchanges are sorted by number of arbitrage events, descending.')
best_exchanges_and_pairs()