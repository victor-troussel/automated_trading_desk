
import db_management as dbm


def get_td_sequential(timeframe_id, candle_array):
    '''
    Inserts td_sequential value of a candle
    INPUT : 
            timeframe_id : a string containing the timeframe 
            candle_array : an array of candles on which we want to get the TD sequential values.
    OUTPUT: 
            TD Sequential values are inserted
    '''
    try:
        previous_candles = dbm.get_previous_candles(timeframe_id, 10, candle_array[0]["symbol"])
        # check that candle is not already stored 
        if not 'td_up' in previous_candles[0]:
            try:
                previous_td = previous_candles[1]['TD']
                previous_ts = previous_candles[1]['TS']
            except:
                previous_td = 0
                previous_ts = 0
            

            td_value = previous_td + 1 if candle_array[0]['close'] > candle_array[4]['close'] else 0
            ts_value = previous_ts + 1 if candle_array[0]['close'] < candle_array[4]['close'] else 0


            interm_td = 0
            interm_ts = 0
            try:
                for i in range(0, previous_candles.count() - 1):
                    if previous_candles[i]['TD'] < previous_candles[i+1]['TD']:
                        interm_td = previous_candles[i]['TD']
                        break
                    elif previous_candles[i]['TS'] < previous_candles[i+1]['TS']:
                        interm_ts = previous_candles[i]['TS']
                        break
            except:
                interm_td = 0
                interm_ts = 0

            td_up = td_value - interm_td
            td_down = ts_value - interm_ts

            dbm.update_candle(timeframe_id, candle_array[0]['symbol'], {'td_up' : td_up})
            dbm.update_candle(timeframe_id, candle_array[0]['symbol'], {'td_down' : td_down})
            dbm.update_candle(timeframe_id, candle_array[0]['symbol'], {'TD' : td_value})
            dbm.update_candle(timeframe_id, candle_array[0]['symbol'], {'TS' : ts_value})

        print('\033[33m' + '>> ' + str(candle_array[0]["symbol"]) + ' \'s TD sequential added for ' + timeframe_id + ' tf. \033[0m')

    except Exception as exception_e:
        print ('\033[31m' + "Unable to compute td_sequential for " + timeframe_id + " timeframe " + '\033[0m')
        print(exception_e)
