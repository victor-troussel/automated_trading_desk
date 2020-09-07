"""
This script aims to compute several Anchored VWAPS taking an array of bitmex candles as an input.
"""
import bitmex, datetime, os, pytz, random, sys, time, warnings
import db_management as dbm

ANCH_VWAP_LOOKBACK_VALUES = [50, 75, 100, 150, 200, 400, 600]


def get_highest_price(candle_array):
	'''
	Returning the highest price on a given period
	'''
	max_price = 0
	for candle in candle_array:
		if candle['high'] > max_price : max_price = candle['high'] 
	return max_price

def get_lowest_price(candle_array):
	'''
	Returning the lowest price on a given period
	'''
	min_price = 1000000000
	for candle in candle_array:
		if candle['low'] < min_price : min_price = candle['low'] 
	return min_price


def get_sma(timeframe_id, candle_location, candle_array):
	'''
	Computes simple moving average, period is given by the length of candle_array
	'''
	price_average = 0
	for candle_item in candle_array:
		price_average += candle_item['high'] if candle_location == 'HIGH' else candle_item['low'] if candle_location == 'LOW' else candle_item['close']
	sma = price_average / len(candle_array)
	try:
		dbm.update_candle(timeframe_id, candle_array[0]['symbol'], {'sma_' + str(len(candle_array)) + '_' + candle_location : sma})
	except Exception as exception_e:
		print("Unable to insert sma for %s timeframe " % timeframe_id)
		print(exception_e)
	return sma


def get_ema(timeframe_id, candle_location, candle_array):
	'''
	Computes exponential moving average, period is given by the length of candle array
	If previous candle doesnt have any ema_value, we use the last sma value
	'''

	current_candle = candle_array[0]
	current_price = current_candle['high'] if candle_location == 'HIGH' else current_candle['low'] if candle_location =='LOW' else current_candle['close'] 
	try:
		previous_candle = dbm.get_previous_candle(timeframe_id, current_candle['symbol'])
	except:
		pass

	try: 
		'ema_' + str(len(candle_array)) + '_' + candle_location in previous_candle
		if ('ema_' + str(len(candle_array)) + '_' + candle_location) in previous_candle:
			previous_ema = previous_candle['ema_' + str(len(candle_array)) + '_' + candle_location]
		else:
			previous_ema = get_sma(timeframe_id, candle_location, candle_array[1:])
	except:
		previous_ema = get_sma(timeframe_id, candle_location, candle_array[1:])


	current_ema = current_price * (2 / (len(candle_array) + 1)) + previous_ema * (1 - (2 / (len(candle_array) + 1)))

	try:
		dbm.update_candle(timeframe_id, current_candle['symbol'], {'ema_' + str(len(candle_array)) + '_' + candle_location : current_ema})
	except Exception as exception_e:
		print("Unable to insert ema for %s timeframe " % timeframe_id)
		print(exception_e)

	return current_ema


def get_anch_vwap_value(timeframe_id, candle_array, lookback_values):
	'''
	Computes the anchored vwaps for every lookback_value taken as an input
	INPUT : 
			an array of candle from Bitmex's API.  
			an array of lookback values
	OUTPUT :
			an array containing the value of every anchored vwap
	'''
	anchored_vwap_values = []
	console_color = "31"

	for lookback_value in lookback_values:

		current_candle = candle_array[0]
		current_volume = current_candle['volume']

		priced_averaged_volume = ((current_candle['low'] + current_candle['high'] + current_candle['close']) / 3) * current_volume
		current_highest = get_highest_price(candle_array[:lookback_value])
		current_lowest = get_lowest_price(candle_array[:lookback_value])

		previous_highest = get_highest_price(candle_array[1:lookback_value])
		previous_lowest = get_lowest_price(candle_array[1:lookback_value])

		is_new_high = previous_highest < current_candle['close'] 
		is_new_low = previous_lowest > current_candle['close']

		'''
		If previous candle has the data we need -> we use it
		else : we start from scratch
		'''
		try:
			previous_candle = dbm.get_previous_candle(timeframe_id, current_candle['symbol'])
			if not previous_candle['volume_sum_high' + str(lookback_value)]:
				previous_candle = candle_array[1]
				previous_candle['volume_sum_high' + str(lookback_value)] = previous_candle['volume']
				previous_candle['price_averaged_volume_sum_high' + str(lookback_value)] = (previous_candle['low'] + previous_candle['high'] +previous_candle['close']) / 3 * previous_candle['volume']
				previous_candle['volume_sum_low' + str(lookback_value)] = previous_candle['volume']
				previous_candle['price_averaged_volume_sum_low' + str(lookback_value)] = (previous_candle['low'] + previous_candle['high'] +previous_candle['close']) / 3 * previous_candle['volume']
		except:
			previous_candle = candle_array[1]
			previous_candle['volume_sum_high' + str(lookback_value)] = previous_candle['volume']
			previous_candle['price_averaged_volume_sum_high' + str(lookback_value)] = (previous_candle['low'] + previous_candle['high'] +previous_candle['close']) / 3 * previous_candle['volume']
			previous_candle['volume_sum_low' + str(lookback_value)] = previous_candle['volume']
			previous_candle['price_averaged_volume_sum_low' + str(lookback_value)] = (previous_candle['low'] + previous_candle['high'] +previous_candle['close']) / 3 * previous_candle['volume']

		volume_sum_high = current_volume if is_new_high else previous_candle['volume_sum_high' + str(lookback_value)] + current_volume
		price_averaged_volume_sum_high = priced_averaged_volume if is_new_high else previous_candle['price_averaged_volume_sum_high' + str(lookback_value)] + priced_averaged_volume

		volume_sum_low = current_volume if is_new_low else previous_candle['volume_sum_low' + str(lookback_value)] + current_volume
		price_averaged_volume_sum_low = priced_averaged_volume if is_new_low else previous_candle['price_averaged_volume_sum_low' + str(lookback_value)] + priced_averaged_volume

		vwap_high = price_averaged_volume_sum_high / volume_sum_high 
		vwap_low = price_averaged_volume_sum_low / volume_sum_low


		ema_high = get_ema(timeframe_id, 'HIGH', candle_array[:lookback_value])
		ema_low = get_ema(timeframe_id, 'LOW', candle_array[:lookback_value])


		vwap_high += ema_high
		vwap_low += ema_low

		vwap_high = vwap_high / 2
		vwap_low = vwap_low /2

		vwap_value = (vwap_high + vwap_low) / 2 

		anchored_vwap_values.append(vwap_value)
		position_from_vwap = "ABOVE" if current_candle["close"] > vwap_value else "BELOW"

		'''
		INSERTING ANCHORED_VWAPS RELATED VALUES
		'''
		try:
			dbm.update_candle(timeframe_id, current_candle['symbol'], {'price_averaged_volume' : priced_averaged_volume})
			dbm.update_candle(timeframe_id, current_candle['symbol'], {'current_highest_' + str(lookback_value) : current_highest})
			dbm.update_candle(timeframe_id, current_candle['symbol'], {'current_lowest_' + str(lookback_value) : current_lowest})
			dbm.update_candle(timeframe_id, current_candle['symbol'], {'previous_highest_' + str(lookback_value) : previous_highest})
			dbm.update_candle(timeframe_id, current_candle['symbol'], {'previous_lowest_' + str(lookback_value) : previous_lowest})
			dbm.update_candle(timeframe_id, current_candle['symbol'], {'volume_sum_high' + str(lookback_value) : volume_sum_high})
			dbm.update_candle(timeframe_id, current_candle['symbol'], {'volume_sum_low' + str(lookback_value) : volume_sum_low})
			dbm.update_candle(timeframe_id, current_candle['symbol'], {'price_averaged_volume_sum_high' + str(lookback_value) : price_averaged_volume_sum_high})
			dbm.update_candle(timeframe_id, current_candle['symbol'], {'price_averaged_volume_sum_low' + str(lookback_value) : price_averaged_volume_sum_low})
			dbm.update_candle(timeframe_id, current_candle['symbol'], {'anchored_vwap' + str(lookback_value) : vwap_value})
			dbm.update_candle(timeframe_id, current_candle['symbol'], {'position_from_vwap' + str(lookback_value) : position_from_vwap})

		except Exception as exception_e:
			print("Unable to update values needed for anchored vwaps for %s timeframe " % timeframe_id)
			print(exception_e)

		print('\033[' + console_color + 'm' + '>> ' + str(current_candle["symbol"]) + ' \'s Anchored VWAPS for ' + str(lookback_value) +' period on a ' + str(timeframe_id) +' timeframe added.' + '\033[0m')

	return anchored_vwap_values








