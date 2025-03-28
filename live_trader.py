import MetaTrader5 as mt5
from datetime import datetime
from data_loader import load_data
from backtester import apply_indicators
import pandas as pd
import json
import time

# Load best strategy
with open("best_strategies.json") as f:
    best_strategy = json.load(f)["best_overall"]["strategy"]

# Connect to MT5
if not mt5.initialize():
    raise Exception("MT5 connection failed")

symbol = "XAUUSD."
timeframe = mt5.TIMEFRAME_M5
lot = 0.1
risk = 1
fixed_sl = 500
fixed_tp = 750
trailing_trigger = 250
trailing_buffer = 200

print(f"[{datetime.now()}] Running live trader using strategy: {best_strategy}")

def check_conditions(df, rule):
    row = df.iloc[-1]
    prev = df.iloc[-2]
    if rule == 'macd_rsi_buy':
        return prev['macd'] < 0 and row['macd'] > 0 and row['rsi'] > 50, "buy"
    elif rule == 'macd_rsi_sell':
        return prev['macd'] > 0 and row['macd'] < 0 and row['rsi'] < 50, "sell"
    elif rule == 'ema_cross_buy':
        return prev['close'] < prev['ema'] and row['close'] > row['ema'], "buy"
    elif rule == 'ema_cross_sell':
        return prev['close'] > prev['ema'] and row['close'] < row['ema'], "sell"
    return False, None

def place_trade(symbol, order_type, lot, atr):
    price = mt5.symbol_info_tick(symbol).ask if order_type == "buy" else mt5.symbol_info_tick(symbol).bid
    deviation = 10
    sl_pips = atr * 2 if atr * 2 < 500 else fixed_sl
    tp_pips = atr * 3 if atr * 2 < 500 else fixed_tp

    sl = price - sl_pips * 0.01 if order_type == "buy" else price + sl_pips * 0.01
    tp = price + tp_pips * 0.01 if order_type == "buy" else price - tp_pips * 0.01

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_BUY if order_type == "buy" else mt5.ORDER_TYPE_SELL,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": deviation,
        "magic": 101010,
        "comment": "AI_STRATEGY_TRADE",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    result = mt5.order_send(request)
    print(f"Trade Result: {result}")

def modify_sl(ticket, new_sl):
    position = mt5.positions_get(ticket=ticket)[0]
    request = {
        "action": mt5.TRADE_ACTION_SLTP,
        "position": ticket,
        "sl": new_sl,
        "tp": position.tp,
        "symbol": position.symbol,
        "magic": 101010,
    }
    result = mt5.order_send(request)
    print(f"SL updated for ticket {ticket}: {result}")

def update_trailing_stops():
    positions = mt5.positions_get(symbol=symbol)
    if positions:
        for pos in positions:
            price = mt5.symbol_info_tick(symbol).bid if pos.type == 1 else mt5.symbol_info_tick(symbol).ask
            open_price = pos.price_open
            if pos.type == 0 and (price - open_price) > trailing_trigger * 0.01:
                new_sl = price - trailing_buffer * 0.01
                if new_sl > pos.sl:
                    modify_sl(pos.ticket, new_sl)
            elif pos.type == 1 and (open_price - price) > trailing_trigger * 0.01:
                new_sl = price + trailing_buffer * 0.01
                if new_sl < pos.sl:
                    modify_sl(pos.ticket, new_sl)

def run_once():
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 100)
    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    df = apply_indicators(df)

    signal, order_type = check_conditions(df, best_strategy)
    if signal:
        print(f"[{datetime.now()}] Signal: {order_type.upper()} confirmed. Placing trade...")
        latest_atr = df.iloc[-1]['atr'] if 'atr' in df.columns else 100
        place_trade(symbol, order_type, lot, latest_atr)
    else:
        print(f"[{datetime.now()}] No trade signal.")

    update_trailing_stops()

if __name__ == "__main__":
    while True:
        run_once()
        time.sleep(5)
