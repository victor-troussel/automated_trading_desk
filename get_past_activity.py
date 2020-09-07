"""
This script aims to connect with Bitmex and to get the last 1000 candles and insert them with additional data in a database.
"""
import bitmex, datetime, os, pytz, sys, time, warnings
import anchored_vwaps as anch_vwaps

import bitmex_data as bitmex_data
import binance_data as binance_data
import ftx_data as ftx_data

import db_management as dbm
import td_sequential as td
warnings.filterwarnings("ignore")



if __name__ == "__main__":

    '''
    Bitmex Data
    '''
    print('\033[35m >>>>> Computing indicators for Bitmex Instruments... \033[0m')
    for timeframe_id in bitmex_data.BITMEX_AVAILABLE_TIMEFRAMES:
        bitmex_client = bitmex_data.connect_bitmex()
        candle_array = bitmex_data.get_ticker_info(bitmex_client, "XBTUSD", timeframe_id)[0]

        #We work with the previous candle in order to have the full and accurate data of a candle
        dbm.insert_candle(timeframe_id, "XBTUSD", candle_array[1])
        vwap_values = anch_vwaps.get_anch_vwap_value(timeframe_id, candle_array[1:], anch_vwaps.ANCH_VWAP_LOOKBACK_VALUES)
        try:
            td.get_td_sequential(timeframe_id, candle_array[1:])
        except Exception as exception_e:
            print ('\033[31m' + "Unable to compute td_sequential for %s timeframe " + '\033[0m' % timeframe_id)
            print(exception_e)
    for i in range(0, len(bitmex_data.BITMEX_AVAILABLE_TIMEFRAMES) * len(anch_vwaps.ANCH_VWAP_LOOKBACK_VALUES) + len(bitmex_data.BITMEX_AVAILABLE_TIMEFRAMES), 1):
        sys.stdout.write("\033[F")
        sys.stdout.write("\033[K") 
    print('\033[33m' + '>> XBTUSD \'s Indicators are up-to-date \033[0m')


    '''
    Binance Data
    '''
    print('\033[35m >>>>> Computing indicators for Binance Instruments... \033[0m')
    for symbol_id in binance_data.BINANCE_WATCH_LIST:
        try:
            for timeframe_id in binance_data.BINANCE_AVAILABLE_TIMEFRAMES:
                candle_array = binance_data.get_ticker_info(symbol_id)
                candle_array[1]["timestamp"] = datetime.datetime.fromtimestamp(candle_array[1]["timestamp"] / 1e3)
                dbm.insert_candle(timeframe_id, symbol_id, candle_array[1])
                vwap_values = anch_vwaps.get_anch_vwap_value(timeframe_id, candle_array[1:], anch_vwaps.ANCH_VWAP_LOOKBACK_VALUES)

                try:
                    td.get_td_sequential(timeframe_id, candle_array[1:])
                except Exception as exception_e:
                    print ('\033[31m' + "Unable to compute td_sequential for %s timeframe " + '\033[0m' % timeframe_id)
                    print(exception_e)

            for i in range(0, len(binance_data.BINANCE_AVAILABLE_TIMEFRAMES) * len(anch_vwaps.ANCH_VWAP_LOOKBACK_VALUES) + len(binance_data.BINANCE_AVAILABLE_TIMEFRAMES), 1):
                sys.stdout.write("\033[F")
                sys.stdout.write("\033[K") 
            print('\033[33m' + '>> ' + symbol_id + ' \'s Indicators are up-to-date \033[0m')

        except Exception as exception_e:
            print("Unable to compute VWAP Values for %s ." % symbol_id)
            print(exception_e)
    

    '''
    FTX Data
    '''
    print('\033[35m >>>>> Computing indicators for FTX Instruments... \033[0m')
    for symbol_id in ftx_data.FTX_WATCH_LIST:
        try:
            for timeframe_id in ftx_data.FTX_AVAILABLE_TIMEFRAMES:
                candle_array = ftx_data.get_ticker_info(symbol_id)
                candle_array[1]["timestamp"] = datetime.datetime.fromtimestamp(candle_array[1]["timestamp"] / 1e3)
                dbm.insert_candle(timeframe_id, symbol_id, candle_array[1])
                vwap_values = anch_vwaps.get_anch_vwap_value(timeframe_id, candle_array[1:], anch_vwaps.ANCH_VWAP_LOOKBACK_VALUES)

                try:
                    td.get_td_sequential(timeframe_id, candle_array[1:])
                except Exception as exception_e:
                    print ('\033[31m' + "Unable to compute td_sequential for %s timeframe " + '\033[0m' % timeframe_id)
                    print(exception_e)

            for i in range(0, len(ftx_data.FTX_AVAILABLE_TIMEFRAMES) * len(anch_vwaps.ANCH_VWAP_LOOKBACK_VALUES) + len(ftx_data.FTX_AVAILABLE_TIMEFRAMES), 1):
                sys.stdout.write("\033[F")
                sys.stdout.write("\033[K") 
            print('\033[33m' + '>> ' + symbol_id + ' \'s Indicators are up-to-date \033[0m')

        except Exception as exception_e:
            print("Unable to compute VWAP Values for %s ." % symbol_id)
            print(exception_e)



