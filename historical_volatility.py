import db_management as dbm

VOLATILITY_LOOKBACK_VALUES = [50, 100, 200, 500]

def get_historical_volatility(timeframe_id, candle_array):
    '''
    Inserts volatility analysis values of a candle
    INPUT : 
            timeframe_id : a string containing the timeframe 
            candle_array : an array of candles on which we want to get the TD sequential values.
    OUTPUT: 
            Volatility values are inserted
    '''

    try:
        previous_candles = dbm.get_previous_candles(timeframe_id, 10, candle_array[0]["symbol"])

        # check that candle is not already stored 

        for lookback_value in VOLATILITY_LOOKBACK_VALUES:
            if not 'volatility' in previous_candles[0]:
                historical_vol = 0
                lookback_value = lookback_value if len(list(candle_array)) > lookback_value else len(list(candle_array))
                for i in range(0, lookback_value):
                    historical_vol += candle_array[i]['high'] / candle_array[i]['low'] * 100

                historical_vol = historical_vol / lookback_value
                dbm.update_candle(timeframe_id, candle_array[0]['symbol'], {'historical_vol_' + str(lookback_value) : historical_vol})



        volatility = candle_array[0]["open"] / candle_array[0]["close"] * 100
        dbm.update_candle(timeframe_id, candle_array[0]['symbol'], {'volatility' : volatility})
        print('\033[33m' + '>> ' + str(candle_array[0]["symbol"]) + ' \'s Volatility analysis for ' + str(lookback_value) + ' periods on a ' + timeframe_id + ' timeframe added. \033[0m')

    except Exception as exception_e:
        print ('\033[31m' + " %s Unable to compute volatility analysis for " + str(candle_array[0]['symbol'])  + " on " +  str(timeframe_id) + " timeframe " + '\033[0m')
        print(exception_e)
