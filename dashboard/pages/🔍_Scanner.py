import asyncio
import aiohttp
import streamlit as st
from datetime import datetime
import config


HEADERS = {
  "X-RapidAPI-Key": st.secrets["headers"],
  "X-RapidAPI-Host": "crypto-arbitrage.p.rapidapi.com"
}

async def make_one_request(url, session):
    LIMIT = asyncio.Semaphore(15)
    async with LIMIT:
        return await session.get(url, headers=HEADERS, ssl=False)

def get_tasks(session):
    tasks = []
    for url in LIST_OF_URLS:
        tasks.append(asyncio.create_task(make_one_request(url, session)))
    return tasks

def print_deals(responses):
    deals_string = ''
    for num, res in enumerate(sorted(responses, key=lambda x: x['arbitrage_profit'], reverse=True), start=1):
        assets = res["pair"].split('/')
        deals_string += f'**ORDER #{num}:**\n' \
                        f'- PAIR: {res["pair"]}\n' \
                        f'- Sell {res["order_sell"]["volume"]} {assets[0]} on {res["order_sell"]["exchange"]} for bid price {res["order_sell"]["bid"]:.10f} {assets[1]}\n' \
                        f'- Buy {res["order_buy"]["volume"]} {assets[0]} on {res["order_buy"]["exchange"]} for bid price {res["order_buy"]["ask"]:.10f} {assets[1]}\n'\
                        f'- PROFIT:  {res["arbitrage_profit"]:.7f}\n' \
                        f'\n'
    st.markdown(deals_string)
    return deals_string

async def get_symbols():
    output = []
    print("Parsing started")
    async with aiohttp.ClientSession() as session:
        tasks = get_tasks(session)
        responses = await asyncio.gather(*tasks)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for response in responses:
            response = await response.json()
            try:
                profit = response['arbitrage_profit']
            except:
                continue

            if profit > 0:
               output.append(response)

        print_deals(output)


st.set_page_config(page_title='SHERLOCK CRYPTO - Scanner',  layout='wide', page_icon=':mag:')
st.title('Crypto arbitrage scanner')
st.markdown('This tool lets you scan for aribtrage opportunities over **50** token pairs on **90** different exchanges.')
st.markdown('Simply choose the desired pairs and exchanges, then click **_Get arbitrage_**. After a short search, you will be provided with a list of orders')

container_pairs = st.container()
all = st.checkbox("Select all pairs")
if all:
    pick_pairs = container_pairs.multiselect("Pairs:", config.PAIRS, config.PAIRS)
else:
    pick_pairs = container_pairs.multiselect("Pairs:", config.PAIRS)

container_exc = st.container()
all = st.checkbox("Select all exchanges")
if all:
    pick_exc = container_pairs.multiselect("Exchanges:", config.EXCHANGES, config.EXCHANGES)
else:
    pick_exc = container_pairs.multiselect("Exchanges:", config.EXCHANGES)

LIST_OF_URLS = []
for p in pick_pairs:
    p = p.split('/')
    LIST_OF_URLS.append(
        f'https://crypto-arbitrage.p.rapidapi.com/crypto-arb?pair={p[0]}%2F{p[1]}&consider_fees=True&selected_exchanges={"%20".join(pick_exc)}'
    )

if st.button('Get arbitrage'):
    with st.spinner('Scanning. Please wait...'):
        asyncio.run(get_symbols())
