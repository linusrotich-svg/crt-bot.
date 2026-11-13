import ccxt
import pandas as pd

class DataFeed:
    def __init__(self):
        # Initialize connection to Binance
        self.exchange = ccxt.binance({
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })
        # Force Sandbox/Testnet mode so we NEVER use real money
        self.exchange.set_sandbox_mode(True)

    def get_candles(self, symbol: str, timeframe: str, limit: int = 100) -> pd.DataFrame:
        """
        Fetches OHLCV data and returns it as a Pandas DataFrame.
        """
        try:
            raw_data = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(raw_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            # Convert timestamp to datetime object for easy reading
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
            
        except Exception as e:
            print(f"[ERROR] Failed to fetch data: {e}")
            return None

# --- QUICK TEST (Runs only if you execute this file directly) ---
if __name__ == "__main__":
    feed = DataFeed()
    print("Fetching M15 data for BTC/USDT...")
    df = feed.get_candles('BTC/USDT', '15m', limit=5)
    if df is not None:
        print(df)
    else:
        print("Failed to fetch data. Check your internet or Binance API access.")