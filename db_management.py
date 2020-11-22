"""
Connections, deletions, insertions and updates in the ["strategies_trades"] database.
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
    database_object = database_object['strategies_trades']
    return database_object, pymongo_client

def get_previous_candle(timeframe_id, symbol):
    """
    Returns the last candle inserted in db for a given timeframe_id / symbol  
    INPUT : timeframe_id, symbol.  
    OUTPUT : last candle object.  
    """
    try:
        pymongo_client, client = connect_db()
        latests_candle = pymongo_client.find({"timeframe": timeframe_id, 'symbol' : symbol}, sort=[('timestamp', -1)])
        client.close()
        return latests_candle[1]
    except Exception as exception_e:
        pass
def get_previous_candles(timeframe_id, n_last_candles, symbol):
    """
    Returns the n_last_candles inserted in db for a given timeframe_id / symbol  
    INPUT : timeframe_id, symbol, n_last_candles.  
    OUTPUT : last candles objects.  
    """
    try:
        pymongo_client, client = connect_db()
        latests_candle = pymongo_client.find({"timeframe": timeframe_id, "symbol" : symbol}, sort=[('timestamp', -1)]).limit(n_last_candles)
        client.close()
        return latests_candle
    except Exception as exception_e:
        print(exception_e)
        pass


def insert_candle(timeframe_id, symbol, candle):
    """
    Inserts a candle object for a given timeframe_id /symbol
    INPUT : timeframe_id, symbol, candle object.  
    OUTPUT : None - candle is inserted.  
    """
    try:
        pymongo_client, client = connect_db()
        candle_item = pymongo_client.find({"symbol" : symbol, "timestamp": candle["timestamp"], "timeframe": timeframe_id})
        does_it_exists = False if candle_item.count() == 0 else True
        if not does_it_exists:
            candle['timeframe'] = timeframe_id
            pymongo_client.insert_one(candle)
            client.close()

    except Exception as exception_e:
        print("Unable to insert current candle for %s timeframe " % timeframe_id)
        print(exception_e)

def update_candle(timeframe_id, symbol, to_be_updated = None):
    """
    Updates a candle object for a given timeframe_id /symbol
    INPUT : timeframe_id, symbol, field(s) to update.  
    OUTPUT : None - candle is updated.  
    """
    try:
        pymongo_client, client = connect_db()
        latest_candle = pymongo_client.find_one({"timeframe": timeframe_id, "symbol" : symbol}, sort=[('timestamp', -1)])
        pymongo_client.update_one({'_id' : latest_candle['_id']}, {'$set' : to_be_updated})
        client.close()

    except Exception as exception_e:
        print("Unable to update latest candle for %s timeframe " % timeframe_id)
        print(exception_e)
def get_candle_by_date(asset, timestamp):
    '''
    Returns nearest candle of a given Asset and timestamp
    INPUT : asset, timestamp
    OUTPUT : None
    '''
    try:
        pymongo_client, client = connect_db()
        nearest_candle = pymongo_client.find_one({"timestamp": timestamp, "symbol" : asset})
        client.close()
        return nearest_candle
    except Exception as exception_e:
        pass



def remove_n_last_candles(timeframe_id, n_last_candles):
    """
    Remove n last candles for a timeframe_id 
    INPUT : timeframe_id, n_last_candles  
    OUTPUT : None - candle is inserted.  
    """
    try:
        pymongo_client, client = connect_db()
        latests_candle = pymongo_client.find({"timeframe": timeframe_id}, sort=[('_id', -1)]).limit(n_last_candles)
        for candle_item in latests_candle:
            pymongo_client.delete_one({ '_id': candle_item['_id'] })
            print("Candle removed : %s  " % str(candle_item["timestamp"]))
        client.close()
    except Exception as exception_e:
        print(exception_e)
        pass


def print_db():
    """
    Print whole database
    INPUT : None
    OUTPUT : None - Database is printed.  
    """
    pymongo_client, client = connect_db()
    for entry in pymongo_client.find():
        print(entry)
        print("\n")
    client.close()


def print_exch_db(exch_name):
    """
    Print whole database for a given exchange.
    INPUT : exch_name
    OUTPUT : None - Database is printed for a given exch_name.  
    """
    pymongo_client, client = connect_db()
    for entry in pymongo_client.find({"exchange" : exch_name}):
        print(entry)
        print("\n")
    client.close()
