import pandas as pd
import pandas_ta_classic as ta

class RiskManager:
    def __init__(self):
        pass

    def calculate_trade(self, df: pd.DataFrame, setup: dict) -> dict:
        """
        Takes the CRT setup and calculates exact Entry, SL, TP1, and TP2.
        Includes an ATR buffer for the Stop Loss and a 1:1.5 Risk/Reward filter.
        """
        if setup is None:
            return None

        # Calculate ATR (Average True Range) for the buffer
        # We use a 14-period ATR on the dataframe
        df['atr'] = ta.atr(df['high'], df['low'], df['close'], length=14)
        current_atr = df.iloc[-1]['atr']
        
        # Define a small buffer (10% of ATR) to avoid fake-out stop hunts
        buffer = current_atr * 0.1

        direction = setup['direction']
        c1_high = setup['c1_high']
        c1_low = setup['c1_low']
        c2_high = setup['c2_high']
        c2_low = setup['c2_low']
        c2_range = setup['c2_range']
        c3_open = setup['c3_open']
        c1_range = c1_high - c1_low

        trade = {}

        if direction == 'SHORT':
            # 1. Entry: C3 Open + 50% of C2 Range
            entry = c3_open + (c2_range * 0.50)
            
            # 2. Stop Loss: C2 High + Buffer
            stop_loss = c2_high + buffer
            
            # 3. Take Profits
            tp1 = entry - (c1_range * 0.50) # 50% of C1
            tp2 = c1_low                    # 100% of C1
            
            # 4. Risk / Reward Math
            risk = stop_loss - entry
            reward = entry - tp2
            
            # Filter: Only take trade if Reward is at least 1.5x Risk
            if reward >= (risk * 1.5):
                trade = {
                    'direction': 'SHORT',
                    'entry': entry,
                    'stop_loss': stop_loss,
                    'tp1': tp1,
                    'tp2': tp2,
                    'risk': risk,
                    'reward': reward
                }

        elif direction == 'LONG':
            # 1. Entry: C3 Open - 50% of C2 Range
            entry = c3_open - (c2_range * 0.50)
            
            # 2. Stop Loss: C2 Low - Buffer
            stop_loss = c2_low - buffer
            
            # 3. Take Profits
            tp1 = entry + (c1_range * 0.50) # 50% of C1
            tp2 = c1_high                   # 100% of C1
            
            # 4. Risk / Reward Math
            risk = entry - stop_loss
            reward = tp2 - entry
            
            # Filter: Only take trade if Reward is at least 1.5x Risk
            if reward >= (risk * 1.5):
                trade = {
                    'direction': 'LONG',
                    'entry': entry,
                    'stop_loss': stop_loss,
                    'tp1': tp1,
                    'tp2': tp2,
                    'risk': risk,
                    'reward': reward
                }

        # If the R:R is too low, it returns an empty dict (trade rejected)
        return trade if trade else None

# --- QUICK TEST ---
if __name__ == "__main__":
    from data_feed import DataFeed
    from crt_engine import CRTEngine
    
    feed = DataFeed()
    engine = CRTEngine()
    risk = RiskManager()
    
    print("Scanning M15 for valid CRT setups and calculating Risk...")
    df = feed.get_candles('BTC/USDT', '15m', limit=100)
    
    if df is not None:
        setup = engine.detect_setup(df)
        
        if setup:
            print(f"\n✅ VALID CRT FOUND: {setup['direction']}")
            trade = risk.calculate_trade(df, setup)
            
            if trade:
                print(f"--- TRADE APPROVED (R:R > 1.5) ---")
                print(f"Direction: {trade['direction']}")
                print(f"Entry:     {trade['entry']:.2f}")
                print(f"Stop Loss: {trade['stop_loss']:.2f}")
                print(f"TP1 (50%): {trade['tp1']:.2f}")
                print(f"TP2 (Full):{trade['tp2']:.2f}")
                print(f"Risk:      {trade['risk']:.2f} | Reward: {trade['reward']:.2f}")
            else:
                print("❌ Trade REJECTED. Risk/Reward is less than 1:1.5.")
        else:
            print("\n❌ No valid CRT setup found on the last closed candles.")