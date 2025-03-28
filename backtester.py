import pandas as pd
import numpy as np
from ta import momentum, trend, volatility

def apply_indicators(df):
    df['rsi'] = momentum.RSIIndicator(df['close'], window=14).rsi()
    df['macd'] = trend.MACD(df['close']).macd_diff()
    df['atr'] = volatility.AverageTrueRange(df['high'], df['low'], df['close']).average_true_range()
    df['ema'] = trend.EMAIndicator(df['close'], window=20).ema_indicator()
    df['ema_fast'] = trend.EMAIndicator(df['close'], window=10).ema_indicator()
    df['ema_slow'] = trend.EMAIndicator(df['close'], window=50).ema_indicator()
    df.dropna(inplace=True)
    return df

def simulate_trades(df, rule, risk_percent=1, balance=10000):
    equity = balance
    risk_per_trade = balance * (risk_percent / 100)
    trade_log = []

    for i in range(1, len(df)):
        row = df.iloc[i]
        prev = df.iloc[i - 1]

        enter_long = False
        enter_short = False

        if rule == 'macd_rsi_buy':
            enter_long = prev['macd'] < 0 and row['macd'] > 0 and row['rsi'] > 50
        elif rule == 'macd_rsi_sell':
            enter_short = prev['macd'] > 0 and row['macd'] < 0 and row['rsi'] < 50
        elif rule == 'ema_cross_buy':
            enter_long = prev['close'] < prev['ema'] and row['close'] > row['ema']
        elif rule == 'ema_cross_sell':
            enter_short = prev['close'] > prev['ema'] and row['close'] < row['ema']
        else:
            continue

        sl = row['atr'] * 2
        tp = row['atr'] * 3
        lot_size = risk_per_trade / sl if sl > 0 else 0

        pnl = tp - sl  # simplified model
        if enter_long:
            equity += pnl * lot_size
            trade_log.append({"type": "buy", "pnl": pnl * lot_size})
        elif enter_short:
            equity += pnl * lot_size
            trade_log.append({"type": "sell", "pnl": pnl * lot_size})

    total_return = equity - balance
    winning_trades = sum(1 for t in trade_log if t['pnl'] > 0)
    win_rate = winning_trades / len(trade_log) if trade_log else 0

    return {
        "initial_balance": balance,
        "final_balance": equity,
        "return": total_return,
        "num_trades": len(trade_log),
        "win_rate": round(win_rate * 100, 2),
        "winning_trades": winning_trades,
        "strategy": rule
    }
