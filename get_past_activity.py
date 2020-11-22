"""
This script aims to connect with Bitmex and to get the last 1000 candles and insert them with additional data in a database.
"""
import bitmex, datetime, os, pytz, sys, time, warnings

import anchored_vwaps as anch_vwaps
import td_sequential as td
import volume_analysis as vol_an
import historical_volatility as hist_volat
import bind_opens as b_opens
import swing_failure_pattern as sfp


import ftx_data as ftx_data

import db_management as dbm
warnings.filterwarnings("ignore")



if __name__ == "__main__":
    '''
    FTX Data
    '''

    print('\033[35m >>>>> Computing indicators for FTX Instruments... \033[0m')
    for symbol_id in ftx_data.FTX_WATCH_LIST:
        try:
            for timeframe_id in ftx_data.FTX_AVAILABLE_TIMEFRAMES:

                candle_array = ftx_data.get_ticker_info(symbol_id, timeframe_id)
                i = 1
                timeframe_min = 60 if timeframe_id == '1h' else 240 if timeframe_id =='4h' else 15
                previous_candles = dbm.get_previous_candles(timeframe_id, 600, symbol_id)
                try:
                    while previous_candles[0]['timestamp'].strftime('%d-%b-%Y-%H:%M') <= (datetime.datetime.fromtimestamp((candle_array[i]['timestamp'] / 1e3)) - datetime.timedelta(minutes = timeframe_min)).strftime('%d-%b-%Y-%H:%M'):
                        i = i + 1

                    for k in reversed(range(1, i, 1)):
                        candle_array[k]["timestamp"] = datetime.datetime.fromtimestamp(candle_array[k]["timestamp"] / 1e3)
                        dbm.insert_candle(timeframe_id, symbol_id, candle_array[k])
                        vwap_values = anch_vwaps.get_anch_vwap_value(timeframe_id, candle_array[k:], anch_vwaps.ANCH_VWAP_LOOKBACK_VALUES)
                        sfp.get_sfp(timeframe_id, candle_array[k:])
                        td.get_td_sequential(timeframe_id, candle_array[k:])
                        hist_volat.get_historical_volatility(timeframe_id, candle_array[k:])
                        b_opens.bind_htf_opens(timeframe_id, candle_array[k:])
                #if there is no related candle in the db
                except:
                    candle_array[1]["timestamp"] = datetime.datetime.fromtimestamp(candle_array[1]["timestamp"] / 1e3)
                    dbm.insert_candle(timeframe_id, symbol_id, candle_array[1])
                    vwap_values = anch_vwaps.get_anch_vwap_value(timeframe_id, candle_array[1:], anch_vwaps.ANCH_VWAP_LOOKBACK_VALUES)
                    sfp.get_sfp(timeframe_id, candle_array[1:])
                    td.get_td_sequential(timeframe_id, candle_array[1:])
                    hist_volat.get_historical_volatility(timeframe_id, candle_array[1:])
                    b_opens.bind_htf_opens(timeframe_id, candle_array[1:])

            print('\033[33m' + '>> ' + symbol_id + ' \'s Indicators are up-to-date \033[0m')

        except Exception as exception_e:
            print("Unable to compute for %s ." % symbol_id)
            print(exception_e)



