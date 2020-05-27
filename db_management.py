"""
Connections, deletions, insertions and updates in the ["bitmex_trading"] database.
"""

from pymongo import MongoClient
from collections import OrderedDict

import sys, warnings

warnings.filterwarnings("ignore")


def connect_db():
    """
    Returns a pymongo client connected to the database.  
    INPUT : None.  
    OUTPUT : database_object, a Mongo client connected on the ["social_posts"] collection of ["veille_strategique"] database.  
    """
    pymongo_client = MongoClient("127.0.0.1", 27017)
    database_object = pymongo_client['trading_data']
    database_object = database_object['bitmex_data']
    return database_object

def get_previous_candle(timeframe_id):
    try:
        pymongo_client = connect_db()
        latests_candle = pymongo_client.find({"timeframe": timeframe_id}, sort=[('timestamp', -1)])
        return latests_candle[1]
    except Exception as exception_e:
        pass
def get_previous_candles(timeframe_id, n_last_candles):
    try:
        pymongo_client = connect_db()
        latests_candle = pymongo_client.find({"timeframe": timeframe_id}, sort=[('timestamp', -1)]).limit(n_last_candles)
        return latests_candle
    except Exception as exception_e:
        print(exception_e)
        pass


def insert_candle(timeframe_id, candle):

    try:
        pymongo_client = connect_db()
        candle_item = pymongo_client.find({"timestamp": candle["timestamp"], "timeframe": timeframe_id})
        does_it_exists = False if candle_item.count() == 0 else True
        if not does_it_exists:
            candle['timeframe'] = timeframe_id
            pymongo_client.insert_one(candle)
    except Exception as exception_e:
        print("Unable to insert current candle for %s timeframe " % timeframe_id)
        print(exception_e)

def update_candle(timeframe_id, to_be_updated = None):
    try:
        pymongo_client = connect_db()
        latest_candle = pymongo_client.find_one({"timeframe": timeframe_id}, sort=[('timestamp', -1)]) 
        pymongo_client.update_one({'_id' : latest_candle['_id']}, {'$set' : to_be_updated})

    except Exception as exception_e:
        print("Unable to update latest candle for %s timeframe " % timeframe_id)
        print(exception_e)



def purge_db():
    pymongo_client = connect_db()
    pymongo_client.drop()

def print_db():
    pymongo_client = connect_db()
    for entry in pymongo_client.find():
        print(entry)
        print("\n\n")