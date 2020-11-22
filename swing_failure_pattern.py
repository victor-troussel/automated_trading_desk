import db_management as dbm

def get_highest_price(candle_array,value):
    '''
    Returning the highest price on a given period
    '''
    try:
        max_price = 0
        for candle in candle_array:
            if candle[value] > max_price : max_price = candle[value] 
        return max_price
    except:
        return 0

def get_lowest_price(candle_array, value):
    '''
    Returning the lowest price on a given period
    '''
    try:
        min_price = 1000000000
        for candle in candle_array:
            if candle[value] < min_price : min_price = candle[value] 
        return min_price
    except:
        return 0

def get_sfp(timeframe_id, candle_array):
    '''
    Inserts swing failure analysis values of a candle
    INPUT : 
            timeframe_id : a string containing the timeframe 
            candle_array : an array of candles on which we want to get the TD sequential values.
    OUTPUT: 
            SFP Analysis values are inserted

    '''
    try:
        
        fractal_top = 0.0
        fractal_bottom = 0.0

        under_lowest = 0.985
        close_lowest = 1
        above_highest = 1.015
        close_highest = 1
        lowest_local = get_lowest_price(candle_array[1:83], 'low')
        highest_local = get_highest_price(candle_array[1:83], 'high')


        is_sfp_up = (candle_array[0]['close'] > (close_lowest * lowest_local)) and (candle_array[0]['low'] < under_lowest * lowest_local) and (candle_array[0]['open'] < candle_array[0]['close'])
        is_sfp_down = (candle_array[0]['close'] < (close_highest * highest_local)) and ((candle_array[0]['high'] > above_highest * highest_local)) and (candle_array[0]['open'] < candle_array[0]['close'])


        dbm.update_candle(timeframe_id, candle_array[0]['symbol'], {'is_sfp_up_' + str(timeframe_id) : is_sfp_up})
        dbm.update_candle(timeframe_id, candle_array[0]['symbol'], {'is_sfp_down_' + str(timeframe_id) : is_sfp_down})
        print('\033[33m' + '>> ' + str(candle_array[0]["symbol"]) + ' \'s SFP analysis for a ' + timeframe_id + ' timeframe added. \033[0m')

    except Exception as exception_e:
        print ('\033[31m' + " %s Unable to compute SFP analysis for " + str(candle_array[0]['symbol'])  + " on " +  str(timeframe_id) + " timeframe " + '\033[0m')
        print(exception_e)
