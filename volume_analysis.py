import db_management as dbm

VOLUME_LOOKBACK_VALUES = [50,100]

def get_volume_analysis(timeframe_id, candle_array):
    '''
    Inserts volume analysis values of a candle
    INPUT : 
            timeframe_id : a string containing the timeframe 
            candle_array : an array of candles on which we want to get the TD sequential values.
    OUTPUT: 
            Volume Analysis values are inserted
    '''

    try:
        previous_candles = dbm.get_previous_candles(timeframe_id, 600, candle_array[0]["symbol"])
        for lookback_value in VOLUME_LOOKBACK_VALUES:

            is_biggest_volume_up = True
            is_biggest_volume_down = True

            lookback_value = lookback_value if previous_candles.count() > lookback_value else previous_candles.count()

            for i in range(0, lookback_value):
                if previous_candles[i]['volume'] * 3 > candle_array[0]['volume'] and candle_array[0]['open'] < candle_array[0]['close']:
                    is_biggest_volume_up = False 
                if previous_candles[i]['volume'] * 3 > candle_array[0]['volume'] and candle_array[0]['open'] > candle_array[0]['close']:
                    is_biggest_volume_down = False 

            dbm.update_candle(timeframe_id, candle_array[0]['symbol'], {'is_biggest_volume_down_' + str(lookback_value) : is_biggest_volume_up})
            dbm.update_candle(timeframe_id, candle_array[0]['symbol'], {'is_biggest_volume_up_' + str(lookback_value) : is_biggest_volume_down})

            print('\033[32m' + '>> ' + str(candle_array[0]["symbol"]) + ' \'s Volume analysis for ' + str(lookback_value) + ' periods on a ' + timeframe_id + ' timeframe added. \033[0m')

    except Exception as exception_e:
        print ('\033[31m' + " %s Unable to compute volume analysis for " + str(candle_array[0]['symbol'])  + " on " +  str(timeframe_id) + " timeframe " + '\033[0m')
        print(exception_e)
