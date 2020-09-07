import bitmex, datetime, os, pytz, sys, time, warnings
import anchored_vwaps as anch_vwaps

import db_management as dbm
import td_sequential as td
warnings.filterwarnings("ignore")

BITMEX_API_KEY ='y8obDjZz7fWXjzO_dSC5VOIc'
BITMEX_API_SECRET = 'Qq6Um_SYIysD_PHYuGyAn9ahYrsJTEVookSrI9hgkUj5OuC9'

BITMEX_AVAILABLE_TIMEFRAMES = ["1h", "1d"]


def connect_bitmex():
    return bitmex.bitmex(test = False, api_key = BITMEX_API_KEY, api_secret = BITMEX_API_SECRET)

def get_user(bitmex_client):
    return bitmex_client.User.User_getMargin().result()

def get_wallet_balance(user_object):
    #Converting sats to $BTC
    return user_object[0]["walletBalance"] / 100000000

def get_ticker_info(bitmex_client, ticker_name, timeframe_id):
    return bitmex_client.Trade.Trade_getBucketed(symbol = ticker_name, binSize = timeframe_id, partial=True, count=700, reverse=True).result()