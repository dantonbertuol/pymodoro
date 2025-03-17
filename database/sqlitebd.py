import sqlite3


class SQLiteDatabase:
    def __init__(self, db_name):
        self.db_name = db_name
        self.connection = None

    def connect(self):
        self.connection = sqlite3.connect(self.db_name)

    def disconnect(self):
        if self.connection:
            self.connection.close()

    def insert(self, object_name, data: dict):
        cursor = self.connection.cursor()
        fields = ", ".join(data.keys())
        placeholders = ", ".join("?" * len(data))
        cursor.execute(f"INSERT INTO {object_name} ({fields}) VALUES ({placeholders})", tuple(data.values()))
        self.connection.commit()

    def find(self, query):
        cursor = self.connection.cursor()
        cursor.execute(query)
        return cursor.fetchall()

    def create_table(self, table_name, columns):
        cursor = self.connection.cursor()
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})")
        self.connection.commit()
