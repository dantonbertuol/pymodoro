from pymongo import MongoClient


class MongoDatabase:
    def __init__(self, uri, db_name):
        self.uri = uri
        self.db_name = db_name
        self.client = None
        self.db = None

    def connect(self):
        self.client = MongoClient(self.uri)
        self.db = self.client[self.db_name]

    def disconnect(self):
        if self.client:
            self.client.close()

    def insert(self, object_name, data):
        collection = self.db[object_name]
        return collection.insert_one(data).inserted_id

    def find(self, query):
        collection = self.db[query["collection"]]
        return collection.find(query["filter"]).sort(query["sort"])

    def create_collection(self, collection_name):
        collections = self.db.list_collection_names()
        if collection_name not in collections:
            self.db.create_collection(name=collection_name, check_exists=True)
