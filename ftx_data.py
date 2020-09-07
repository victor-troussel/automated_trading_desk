import hmac, json, requests, time
from requests import Request

FTX_API_KEY = "I82URa0CXtNoRAZw3qpl1U3Erhu2P0k_XtKykBo2"
FTX_API_SECRET = "PvRXtFwcoLOGcH-fzlkK7C8_4ErKk9owgu3moZxq"

FTX_AVAILABLE_TIMEFRAMES = ["1h"]


FTX_WATCH_LIST = ["TRX-PERP", "OKB-PERP", "LINK-PERP", "AMPL-PERP", "DEFI-PERP", "ALGO-PERP", "SOL-PERP", "DOT-PERP"]





def connect_ftx():
    return requests.Session()


def get_ticker_info(symbol_id):
    requests_session = connect_ftx()


    ts = int(time.time() * 1000)
    request = Request('GET', 'https://ftx.com/api/markets/' + symbol_id + '/candles?resolution=3600&limit=700')
    prepared = request.prepare()
    signature_payload = f'{ts}{prepared.method}{prepared.path_url}'.encode()
    signature = hmac.new(FTX_API_SECRET.encode(), signature_payload, 'sha256').hexdigest()

    request.headers['FTX-KEY'] = FTX_API_KEY
    request.headers['FTX-SIGN'] = signature
    request.headers['FTX-TS'] = str(ts)

    last_candles = json.loads(requests_session.send(request.prepare()).text)

    candles_array = []

    for candle_item in last_candles.get('result'):
        candle_dict = {}
        candle_dict["symbol"] = symbol_id
        candle_dict["timestamp"] = float(candle_item["time"])
        candle_dict["open"] = float(candle_item["open"])
        candle_dict["high"] = float(candle_item["high"])
        candle_dict["low"] = float(candle_item["low"])
        candle_dict["close"] = float(candle_item["close"])
        candle_dict["volume"] = float(candle_item["volume"])
        candle_dict["exchange"] = "FTX"

        candles_array.append(candle_dict)
    candles_array = candles_array[::-1]
    return candles_array


