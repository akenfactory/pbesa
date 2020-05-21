import pymongo

from pymongo import MongoClient
from ...kernel.adapter.Adapter import Adapter

class MongoAdapter(AdapTK):

    db = None
    conf = None
    client = None

    def __init__(self, conf):
        self.conf = conf
        super().__init__()

    def setUp(self):
        self.client = MongoClient()
        self.db = self.client[self.conf['database']]

    def response(self, response):
        pass
    
    def request(self):
        pass
        
    def finalize(self):
        pass

    def getAll(self, collection):
        coll = self.db[collection]
        return coll.find()

    def getObject(self, collection, query):
        coll = self.db[collection]
        return coll.find_one(query)

    def getObjectByID(self, collection, id):
        coll = self.db[collection]
        return coll.find_one({"_id": id})

    def insertObject(self, collection, dto):
        coll = self.db[collection]
        return coll.insert_one(dto).inserted_id

    def updateObject(self, collection, id, dto):
        coll = self.db[collection]
        return coll.replace_one({"_id": id}, dto, True)
