import sqlite3


class ScraperDatabase:
    def __init__(self, db_name: str):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()


    def create_table(self, name):
        self.conn = sqlite3.connect('db/scraping.db')
        self.cur = self.conn.cursor()

        self.cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                filter_url TEXT,
                title TEXT,
                price TEXT,
                url TEXT UNIQUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        self.conn.commit()
        self.conn.close()


    def add_data(self, name, user_id, filter_url, title, price, url):
        self.conn = sqlite3.connect('db/scraping.db')
        self.cur = self.conn.cursor()

        self.cur.execute(
            f"""
            INSERT INTO {name} (user_id, filter_url, title, price, url)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, filter_url, title, price, url)
        )
        self.conn.commit()
        self.conn.close()


    def exists(self, table_name: str, url: str) -> bool:
        self.conn = sqlite3.connect('db/scraping.db')
        self.cur = self.conn.cursor()

        self.cur.execute(
            f"SELECT 1 FROM {table_name} WHERE url = ? LIMIT 1",
            (url,)
        )
        exists = self.cur.fetchone() is not None

        self.conn.close()
        return exists
    

db = ScraperDatabase('db/scraping.db')


