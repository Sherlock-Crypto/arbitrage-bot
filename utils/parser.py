import asyncio
import aiohttp
from datetime import datetime
import pytz
from utils.db import BotDB

tz = pytz.timezone('Europe/Moscow')


class Parser(BotDB):
    def __init__(self, pairs, exchanges, headers, db_file=None):
        BotDB.__init__(self, db_file)

        self.limit = asyncio.Semaphore(10)
        self.pairs = pairs
        self.exchanges = exchanges
        self.headers = headers
        self.list_of_urls = []

        for p in self.pairs:
            p = p.split('/')
            self.list_of_urls.append(
                f'https://crypto-arbitrage.p.rapidapi.com/crypto-arb?pair={p[0]}%2F{p[1]}&consider_fees=True&selected_exchanges={"%20".join(exchanges)}'
            )


    async def make_one_request(self, url, session):
        async with self.limit:
            return await session.get(url, headers=self.headers, ssl=False)

    def get_tasks(self, session):
        tasks = []
        for url in self.list_of_urls:
            tasks.append(asyncio.create_task(self.make_one_request(url, session)))
        return tasks

    def print_dict(self, dct):
        top_string = f'[{self.timestamp}]\n<b>TOP EXCHANGES TO ACCOMMODATE LIQUIDITY:</b>\n'
        for item, amount in dct.items():
            top_string += "{} ({})\n".format(item, amount)
        return top_string

    def print_deals(self):
        deals_string = f'[{self.timestamp}]\n<b>ARBITRAGE DEALS:</b>\n'
        for num, line in enumerate(sorted(self.lines, key=lambda x: x[8], reverse=True), start=1):
            assets = line[1].split('/')
            deals_string += f'<b>ORDER #{num}:</b>\n' \
                            f'Pair - {line[1]}\n' \
                            f'Sell {line[6]} {assets[0]} on {line[2]} for bid price {line[4]:.10f} {assets[1]}\n' \
                            f'Buy {line[7]} {assets[0]} on {line[3]} for ask price {line[5]:.10f} {assets[1]}\n'\
                            f'<u>PROFIT:</u>  {line[8]:.7f}\n' \
                            f'\n'
        return deals_string


    async def get_symbols(self):
        self.lines = []
        print("Parsing started")
        self.top_exchanges = dict()
        async with aiohttp.ClientSession() as session:
            tasks = self.get_tasks(session)
            responses = await asyncio.gather(*tasks)
            self.timestamp = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
            for response in responses:
                response = await response.json()
                print(response)
                try:
                    profit = response['arbitrage_profit']
                except:
                    continue

                if profit > 0:
                    self.lines.append([self.timestamp,
                                       response['pair'],
                                       response['order_sell']['exchange'],
                                       response['order_buy']['exchange'],
                                       response['order_sell']['bid'],
                                       response['order_buy']['ask'],
                                       response['order_sell']['volume'],
                                       response['order_buy']['volume'],
                                       response['arbitrage_profit']])
        if self.lines:
            print('Got responses')
            for row in self.lines:
                self.insert_row(row)
                if row[2] in self.top_exchanges.keys():
                    self.top_exchanges[row[2]] += 1
                else:
                    self.top_exchanges[row[2]] = 1
                if row[3] in self.top_exchanges.keys():
                    self.top_exchanges[row[3]] += 1
                else:
                    self.top_exchanges[row[3]] = 1
            print('Inserted all rows')

        self.top_exchanges = self.print_dict(dict(sorted(self.top_exchanges.items(), key=lambda item: item[1], reverse=True)))
        self.orders = self.print_deals()
        return(self.top_exchanges, self.orders)
