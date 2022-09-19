import os
path = os.path.dirname(__file__)

PARSE_INTERVAL = 10

RAPID_API_KEY = os.getenv('RAPID_API_KEY')
API_TOKEN = os.getenv('API_TOKEN')
DB_URI = os.getenv('DATABASE_URL')

with open(path+'/data/exchanges.txt', 'r') as f:
    EXCHANGES = f.read().split(', ')

with open(path+'/data/pairs.txt', 'r') as f:
    PAIRS = f.read().split(' ')

HEADERS = {
  "X-RapidAPI-Key": RAPID_API_KEY,
  "X-RapidAPI-Host": "crypto-arbitrage.p.rapidapi.com"
}