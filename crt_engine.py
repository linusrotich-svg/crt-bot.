import pandas as pd

class CRTEngine:
    def __init__(self):
        pass

    def detect_setup(self, df: pd.DataFrame) -> dict:
        """
        Analyzes the last 3 closed candles to find a valid CRT setup.
        Returns a dictionary with setup details, or None if no setup is found.
        """
        if df is None or len(df) < 4:
            return None

        # We use iloc to grab specific rows from the bottom of the DataFrame.
        # -1 is the current LIVE candle (forming).
        # -2, -3, -4 are the last 3 FULLY CLOSED candles.
        c1 = df.iloc[-4] # Candle 1: The Range
        c2 = df.iloc[-3] # Candle 2: The Sweep (Turtle Soup)
        c3 = df.iloc[-2] # Candle 3: The Trigger

        # --- BEARISH CRT (SHORT) ---
        # 1. C2 High sweeps above C1 High
        # 2. C2 Close is back INSIDE C1 range
        # 3. C2 Low did NOT sweep below C1 Low (One-sided sweep only)
        if (c2['high'] > c1['high'] and 
            c2['close'] < c1['high'] and 
            c2['low'] >= c1['low']):
            
            return {
                'direction': 'SHORT',
                'c1_high': c1['high'],
                'c1_low': c1['low'],
                'c2_high': c2['high'],
                'c2_low': c2['low'],
                'c2_range': c2['high'] - c2['low'],
                'c3_open': c3['open']
            }

        # --- BULLISH CRT (LONG) ---
        # 1. C2 Low sweeps below C1 Low
        # 2. C2 Close is back INSIDE C1 range
        # 3. C2 High did NOT sweep above C1 High (One-sided sweep only)
        elif (c2['low'] < c1['low'] and 
              c2['close'] > c1['low'] and 
              c2['high'] <= c1['high']):
            
            return {
                'direction': 'LONG',
                'c1_high': c1['high'],
                'c1_low': c1['low'],
                'c2_high': c2['high'],
                'c2_low': c2['low'],
                'c2_range': c2['high'] - c2['low'],
                'c3_open': c3['open']
            }

        # If neither condition is met, return None
        return None

# --- QUICK TEST ---
if __name__ == "__main__":
    from data_feed import DataFeed
    
    feed = DataFeed()
    engine = CRTEngine()
    
    print("Scanning M15 for valid CRT setups...")
    df = feed.get_candles('BTC/USDT', '15m', limit=10)
    
    if df is not None:
        setup = engine.detect_setup(df)
        
        if setup:
            print(f"\n✅ VALID CRT FOUND: {setup['direction']}")
            print(f"C1 Range: {setup['c1_low']} to {setup['c1_high']}")
            print(f"C2 Range: {setup['c2_low']} to {setup['c2_high']}")
            print(f"C3 Open: {setup['c3_open']}")
        else:
            print("\n❌ No valid CRT setup found on the last closed candles.")
    else:
        print("Could not run scan because data feed failed.") 