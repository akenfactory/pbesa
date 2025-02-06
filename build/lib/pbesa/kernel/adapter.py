# -*- coding: utf-8 -*-
"""
----------------------------------------------------------
-------------------------- PBESA -------------------------
----------------------------------------------------------

@autor AKEN
@version 4.0.0
@date 08/08/24
"""

# --------------------------------------------------------
# Define resources
# --------------------------------------------------------

from pymongo import MongoClient
from pymongo.cursor import Cursor
from abc import ABC, abstractmethod
from .io.system_file import SystemFile

# --------------------------------------------------------
# Define Adapter component
# --------------------------------------------------------

class Adapter(ABC):
    """ Base adapter class """
    
    # Adapter data
    data = None
    # Adapter configuration
    config = None
    
    def __init__(self) -> None:
        """ Constructor """
        super().__init__()

    @abstractmethod
    def setup(self) -> None:
        """ Set up adapter """
        pass

    @abstractmethod
    def response(self) -> None:
        """ Response adapter """
        pass
    
    @abstractmethod
    def request(self) -> None:
        """ Request adapter """
        pass

    @abstractmethod
    def finalize(self) -> None:
        """ Finalize adapter """
        pass

# --------------------------------------------------------
# Define FileAdapter component
# --------------------------------------------------------

class FileAdapter(Adapter):
    """ File adapter class """

    def __init__(self, config) -> None:
        """ Constructor 
        :param config: Configuration
        """
        self.config = config
        super().__init__()

    def setup(self) -> None:
        """ Set up adapter """
        if self.config['type'] == 'JSON':            
            sf = SystemFile(self.config['path'])
            self.data = sf.read_json_file()

    def response(self) -> None:
        """ Response adapter """
        pass
    
    def request(self):
        """ Request adapter """
        return self.data

    def finalize(self):
        """ Finalize adapter """
        pass

# --------------------------------------------------------
# Define MongoAdapter component
# --------------------------------------------------------

class MongoAdapter(Adapter):
    """ Mongo adapter class """

    # Database
    db = None
    # Configuration
    conf = None
    # Client
    client = None

    def __init__(self, conf:dict) -> None:
        """ Constructor
        :param conf: Configuration
        """
        self.conf = conf
        super().__init__()

    def setup(self) -> None:
        """ Set up adapter """
        self.client = MongoClient()
        self.db = self.client[self.conf['database']]

    def response(self, response:str) -> None:
        """ Response adapter """
        pass
    
    def request(self) -> None:
        """ Request adapter """
        pass
        
    def finalize(self) -> None:
        """ Finalize adapter """
        pass

    def get_all(self, collection:str) -> Cursor:
        """ Get all objects from collection
        :param collection: Collection
        """
        coll = self.db[collection]
        return coll.find()

    def get_object(self, collection:str, query:dict) -> any:
        """ Get object from collection
        :param collection: Collection
        :param query: Query
        """
        coll = self.db[collection]
        return coll.find_one(query)

    def get_object_by_id(self, collection:str, id:str) -> any:
        """ Get object from collection by ID
        :param collection: Collection
        :param id: ID
        """
        coll = self.db[collection]
        return coll.find_one({"_id": id})

    def insert_object(self, collection:str, dto:dict) -> None:
        """ Insert object in collection
        :param collection: Collection
        :param dto: Data transfer object
        """
        coll = self.db[collection]
        return coll.insert_one(dto).inserted_id

    def update_object(self, collection:str, id:str, dto:dict) -> None:
        """ Update object in collection
        :param collection: Collection
        :param id: ID
        :param dto: Data transfer object
        """
        coll = self.db[collection]
        return coll.replace_one({"_id": id}, dto, True)