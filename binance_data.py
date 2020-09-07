from binance.client import Client
from pprint import pprint
from operator import itemgetter, attrgetter

import anchored_vwaps as anch_vwaps
import db_management as dbm
import datetime

api_key = "jNPno6ZanVws5GIvT9RtsmWI9R5u9AZfSekYWdY06QSSQfo5Hli87mJPYO7ZJWEX"
api_secret ="Qp9YBhPdhtxLBdrddLL3T5o0pJ4Ka4wvehteeMNEgVd9A5JD9IydrOW4bEa6Ggb5"

BINANCE_AVAILABLE_TIMEFRAMES = ["1h"]
BINANCE_WATCH_LIST = ["LINKUSDT", "CHZUSDT", "EOSUSDT", "ADAUSDT", "BNBUSDT", "XTZUSDT", "SOLUSDT", "ANKRUSDT", "MATICUSDT", "XMRUSDT"]

def connect_binance():
    return Client(api_key, api_secret)


def get_ticker_info(pair_name):

    binance_client = connect_binance()
    last_candles = binance_client.get_klines(symbol= pair_name, interval= Client.KLINE_INTERVAL_1HOUR, limit = 700)



    candles_array = []

    for candle_item in last_candles:
        candle_dict = {}
        candle_dict["symbol"] = pair_name
        candle_dict["timestamp"] = float(candle_item[0])
        candle_dict["open"] = float(candle_item[1])
        candle_dict["high"] = float(candle_item[2])
        candle_dict["low"] = float(candle_item[3])
        candle_dict["close"] = float(candle_item[4])
        candle_dict["volume"] = float(candle_item[5])
        candle_dict["exchange"] = "BINANCE"

        candles_array.append(candle_dict)
    
    candles_array = candles_array[::-1]

    return candles_array

def get_agg_trades(pair_name):
    binance_client = connect_binance()
    agg_trades = binance_client.get_aggregate_trades(symbol=pair_name, limit =100)
    btc_price = float(get_ticker_price("BTCUSDT"))

    now = datetime.datetime.now()
    delta = datetime.timedelta(minutes = 3)

    for agg_trade in agg_trades:
        trade_date = datetime.datetime.fromtimestamp(agg_trade["T"] / 1000)
        if trade_date + delta > now:
            if not "USD" in pair_name:
                if ((float(agg_trade["p"]) * float(btc_price)) * float(agg_trade["q"])) > 60000 and not agg_trade["m"]:
                    agg_trade["usd_p"] = btc_price * float(agg_trade["p"])
                    agg_trade["pair_name"] = pair_name
                    agg_trade["date"] = trade_date
                    return agg_trade
            else:
                if (float(agg_trade["p"])* float(agg_trade["q"])) > 60000 and not agg_trade["m"]:
                    agg_trade["usd_p"] = agg_trade["p"]
                    agg_trade["pair_name"] = pair_name
                    agg_trade["date"] = trade_date
                    return agg_trade

def get_all_tickers_by_pair(pair_name):
    binance_client = connect_binance()
    tickers_list = binance_client.get_all_tickers()
    real_tickers = []
    for ticker_name in tickers_list:
        if ticker_name["symbol"].endswith(pair_name):
            if float(ticker_name["price"]) > 0.000001:
               real_tickers.append(ticker_name["symbol"])
    return real_tickers


def get_all_tickers_and_prices(pair_name):
    binance_client = connect_binance()
    tickers_list = binance_client.get_all_tickers()
    real_tickers = []
    for ticker_name in tickers_list:
        if ticker_name["symbol"].endswith(pair_name):
            real_tickers.append(ticker_name)
    return real_tickers

def get_ticker_price(symbol_id):
    binance_client = connect_binance()
    return binance_client.get_avg_price(symbol= symbol_id)['price']


