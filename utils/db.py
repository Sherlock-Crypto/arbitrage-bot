import psycopg2


class BotDB:
    def __init__(self, DB_URI):
        self.connection = psycopg2.connect(DB_URI, sslmode='require')
        self.cursor = self.connection.cursor()
        print('Connected to database')

    def insert_row(self, row):
        self.cursor.execute(
            "INSERT INTO events(timestamp, pair, sell_at, buy_at, sell_price_bid, buy_price_ask, sell_volume, buy_volume, profit) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)", row)
        self.connection.commit()

    def get_subscriptions(self):
        with self.connection:
            self.cursor.execute("SELECT * FROM subscriptions WHERE status = TRUE")
            return self.cursor.fetchall()

    def subscriber_exists(self, user_id):
        with self.connection:
            self.cursor.execute('SELECT * FROM subscriptions WHERE user_id = %s', (user_id,))
            return bool(len(self.cursor.fetchall()))

    def add_subscriber(self, user_id, status = True):
        with self.connection:
            return self.cursor.execute("INSERT INTO subscriptions (user_id, status) VALUES(%s,%s)", (user_id,status))

    def update_subscription(self, user_id, status):
        with self.connection:
            return self.cursor.execute("UPDATE subscriptions SET status = %s WHERE user_id = %s", (status, user_id))

    def close(self):
        self.connection.close()

    def get_all(self):
        result = self.cursor.execute("SELECT * FROM events ORDER BY timestamp")
        return result.fetchall()