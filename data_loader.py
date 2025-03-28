import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta

def load_data(symbol="XAUUSD.", timeframe=mt5.TIMEFRAME_M5, days_back=90):
    if not mt5.initialize():
        raise RuntimeError("MT5 Initialization failed")

    from_date = datetime.now() - timedelta(days=days_back)
    rates = mt5.copy_rates_from(symbol, timeframe, from_date, days_back * 24 * 12)
    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    return df