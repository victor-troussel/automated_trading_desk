import db_management as dbm
import pendulum, time
import bitmex
def bind_htf_opens(timeframe_id, candle_array):
    '''
    Inserts opens of HTF for this asset
    INPUT : 
            timeframe_id : a string containing the timeframe 
            candle_array : an array of candles on which we want to get the TD sequential values.
    OUTPUT: 
            None : weeklyOpen and monthlyOpen are inserted in the database.
    '''
    try:
        wOpen_date = (pendulum.instance(candle_array[0]['timestamp']).start_of('week'))
        mOpen_date = (pendulum.instance(candle_array[0]['timestamp']).start_of('month'))
        try:
            wOpen = dbm.get_candle_by_date(candle_array[0]['symbol'], wOpen_date)['open']
            mOpen = dbm.get_candle_by_date(candle_array[0]['symbol'], wOpen_date)['open']
            dbm.update_candle(timeframe_id, candle_array[0]['symbol'], {'wOpen' : wOpen})
            dbm.update_candle(timeframe_id, candle_array[0]['symbol'], {'mOpen' : wOpen})
        except:
            pass
        print('\033[33m' + '>> ' + str(candle_array[0]["symbol"]) + ' \'s Monthly & Weekly opens inserted. \033[0m')

    except Exception as exception_e:
        print ('\033[31m' + " %s Unable to compute wOpen and mOpen analysis for " + str(candle_array[0]['symbol'])  + " on " +  str(timeframe_id) + " timeframe " + '\033[0m')
        print(exception_e)





