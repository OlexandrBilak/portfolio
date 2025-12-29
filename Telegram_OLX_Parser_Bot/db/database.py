import sqlite3

TABLE_PREFIX = {
    "new_listing": 100,
    "price_change": 200,
    "vacancies": 300,
}

def generate_global_id(cur, table_name: str) -> int:
    prefix = TABLE_PREFIX[table_name]

    cur.execute(
        f"SELECT MAX(global_id) FROM {table_name}"
    )
    last_id = cur.fetchone()[0]

    if last_id is None:
        return prefix + 1

    return last_id + 1


class Database:
    def __init__(self, db_name: str):
        self.conn = sqlite3.connect(db_name)
        self.cur = self.conn.cursor()

    def create_table(self, name):
        self.conn = sqlite3.connect('db/subscriptions.db')
        self.cur = self.conn.cursor()

        self.cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                global_id INTEGER UNIQUE,
                user_id INTEGER,
                type TEXT,
                url TEXT,
                interval INTEGER, 
                last_value TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        self.conn.commit()
        self.conn.close()


    def add_data(self, name, user_id, type, url, interval, last_value):
        self.conn = sqlite3.connect('db/subscriptions.db')
        self.cur = self.conn.cursor()

        global_id = generate_global_id(self.cur, name)

        self.cur.execute(
            f"""
            INSERT INTO {name} (global_id, user_id, type, url, interval, last_value)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (global_id, user_id, type, url, interval, last_value)
        )
        self.conn.commit()
        self.conn.close()


    def get_data(self, name, user_id):
        self.conn = sqlite3.connect("db/subscriptions.db")
        self.cur = self.conn.cursor()
        
        self.cur.execute(
            f"""
            SELECT * FROM {name} WHERE user_id = ?
            """,
            (user_id,)
        )
        return self.cur.fetchall()
        

    def delete_data(self,user_id, global_id):
        self.conn = sqlite3.connect('db/subscriptions.db')
        self.cur = self.conn.cursor()

        tables = ["new_listing", "price_change", "vacancies"]
        deleted = 0

        
        for table in tables:
            self.cur.execute(
                f"""
                DELETE FROM {table} WHERE global_id = ? AND user_id = ?
                """,
                (global_id, user_id)
            )
            deleted += self.cur.rowcount

        if deleted > 0:
            result = "Підписку видалено 🗑"
        else:
            result = "Підписку не знайдено 🤔"
        
        self.conn.commit()
        self.conn.close()

        return result



    def update_interval(self, interval, user_id, global_id):
        self.conn = sqlite3.connect('db/subscriptions.db')
        self.cur = self.conn.cursor()

        tables = ["new_listing", "price_change", "vacancies"]
        updated = 0

        
        for table in tables:
            self.cur.execute(
                f"""
                UPDATE {table} SET interval = ? WHERE global_id = ? AND user_id = ?
                """,
                (interval, global_id, user_id)
            )
            updated += self.cur.rowcount

        if updated > 0:
            result = "Інтервал оновлено ✅"
        else:
            result = "Підписку не знайдено 🤔"

        self.conn.commit()
        self.conn.close()

        return result
    

    def update_url(self, url, user_id, global_id):
        self.conn = sqlite3.connect('db/subscriptions.db')
        self.cur = self.conn.cursor()

        tables = ["new_listing", "price_change", "vacancies"]
        updated = 0

        
        for table in tables:
            self.cur.execute(
                f"""
                UPDATE {table} SET url = ? WHERE global_id = ? AND user_id = ?
                """,
                (url, global_id, user_id)
            )
            updated += self.cur.rowcount

        if updated > 0:
            result = "URL оновлено ✅"
        else:
            result = "Підписку не знайдено 🤔"

        self.conn.commit()
        self.conn.close()

        return result


    def get_all_data(self, user_id):
        self.conn = sqlite3.connect('db/subscriptions.db')
        self.cur = self.conn.cursor()

        tables = ["new_listing", "price_change", "vacancies"]
        result = []
        
        for table in tables:
            self.cur.execute(
                f"SELECT *, '{table}' as table_name FROM {table} WHERE user_id = ?",
                (user_id,)
            )
            result.extend(self.cur.fetchall())

        self.conn.close()
        return result


db = Database('db/subscriptions.db')
