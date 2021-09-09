import websocket, json, pprint, talib, numpy
import config
from binance.client import Client
from binance.enums import *
SOCKET = "wss://stream.binance.us:9443/ws/ethusd@kline_1m"

RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
TRADE_SYMBOL = 'ETHUSD'
TRADE_QUANTITY = 0.05


closes = []
in_position = False

client = Client(config.API_KEY, config.API_SECRET, tld='us')

def order(symbol, quantity, side, order_type=ORDER_TYPE_MARKET):
    try:
        print("sending order")
        order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)
        return True
    except Exception as e:
        return False

    return True


def on_open(ws):
    print('Opened Connection')

def on_close(ws):
    print('Closed Connection')

def on_message(ws, message):
    global closes
    print('Received Message')
    print(message)
    json_message = json.loads(message)
    print(json_message)
    pprint.pprint(json_message)

    candle = json_message['k']

    is_candle_closed = candle['x']
    close = candle['c']

    if is_candle_closed:
        print("candle closed at {}".format(close))
        closes.append(float(close))
        print('Closes')
        print(closes)

        if len(closes) > RSI_PERIOD:
            np_closes = numpy.array(closes)
            rsi = talib.RSI(np_closes, RSI_PERIOD)
            print("All rsi's calculated so far")
            print(rsi)
            last_rsi = rsi[-1]
            print("the current rsi is {}".format(last_rsi))

            if last_rsi > RSI_OVERBOUGHT: 
                if in_position:
                     print("Sell, my dude.")
                     #order sell logic
                     order_succeeded = order(TRADE_SYMBOL, TRADE_QUANTITY, SIDE_SELL)
                     if order_succeeded:
                         in_position = False
                else:
                    print("it is overbought, but we don't own any")

            if last_rsi < RSI_OVERSOLD:
                if in_position: 
                    print("It is oversold, but you already own it. Chill.")
                else:
                    print("Buy, my dude.")
                    #put binance order buy logic here
                    order_succeeded = order(TRADE_SYMBOL, TRADE_QUANTITY, SIDE_BUY)
                    if order_succeeded:
                        in_position = True


ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()