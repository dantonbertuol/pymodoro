from database.mongobd import MongoDatabase
from database.sqlitebd import SQLiteDatabase
from conf import SQLITE_DATABASE_PATH, MONGODB_HOST, MONGODB_USER, MONGODB_PASSWORD, DB_NAME


class Database:
    def __init__(self, db_type):
        self.db_type = db_type
        self.db = None

    def connect(self):
        if self.db_type == "sqlite":
            self.db = SQLiteDatabase(SQLITE_DATABASE_PATH)
        elif self.db_type == "mongodb":
            user = MONGODB_USER
            password = MONGODB_PASSWORD
            host = MONGODB_HOST
            database = DB_NAME
            self.db = MongoDatabase(
                uri=f"mongodb+srv://{user}:{password}@{host}",
                db_name=database,
            )
        self.db.connect()

    def create_structure(self):
        if self.db_type == "sqlite":
            self.db.create_table(
                "pomodoros",
                """
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT,
                duration_seconds INTEGER NOT NULL,
                created_date DATETIME NOT NULL,
                type TEXT NOT NULL
                """,
            )
        elif self.db_type == "mongodb":
            self.db.create_collection("pomodoros")

    def insert_data(self, data: dict):
        self.db.insert("pomodoros", data)

    def get_pomodors(self):
        if self.db_type == "sqlite":
            results = self.db.find(
                "SELECT DISTINCT task FROM pomodoros where task is not null and task != '' ORDER BY id DESC"
            )
            return [row[0] for row in results]
        elif self.db_type == "mongodb":
            try:
                return self.db.find(
                    {"collection": "pomodoros", "filter": {"task": {"$ne": ""}}, "sort": {"_id": -1}}
                ).distinct("task")
            except Exception:
                return []

    def disconnect(self):
        self.db.disconnect()
