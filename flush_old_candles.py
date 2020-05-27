import db_management as dbm
import datetime
def flush_1m(older_than_n_days):
    delta = datetime.timedelta(days = older_than_n_days)
    array_candles = dbm.get_previous_candles("1m", 7000)
    for candle_item in array_candles:
        if candle_item["timestamp"] + delta < datetime.datetime.now():
            pymongo_client = dbm.connect_db()
            pymongo_client.delete_one({ '_id': candle_item['_id'] })
            print("Candle removed : %s  " % str(candle_item["timestamp"]))
def flush_5m(older_than_n_days):
    delta = datetime.timedelta(days = older_than_n_days)
    array_candles = dbm.get_previous_candles("5m", 7000)
    for candle_item in array_candles:
        if candle_item["timestamp"] + delta < datetime.datetime.now():
            pymongo_client = dbm.connect_db()
            pymongo_client.delete_one({ '_id': candle_item['_id'] })
            print("Candle removed : %s  " % str(candle_item["timestamp"]))

flush_1m(3)
flush_5m(15)