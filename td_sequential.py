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
        print("Parsing candles to compute TD sequential on a %s timeframe." % timeframe_id)
        previous_candles = dbm.get_previous_candles(timeframe_id, 600)

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

        dbm.update_candle(timeframe_id, {'td_up' : td_up})
        dbm.update_candle(timeframe_id, {'td_down' : td_down})
        dbm.update_candle(timeframe_id, {'TD' : td_value})
        dbm.update_candle(timeframe_id, {'TS' : ts_value})

        print(">>> TD sequential added for %s tf." % timeframe_id)

    except Exception as exception_e:
        print(exception_e)

