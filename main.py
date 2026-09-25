import numpy as np
import pandas as pd
from tabulate import tabulate

class OFIBacktester:
    """
    Event-Driven Microstructure Backtester utilizing Order Flow Imbalance (OFI)
    for high-frequency short-term direction prediction.
    """
    def __init__(self, df, ofi_threshold=0.35, transaction_cost=0.0001):
        self.df = df.copy()
        self.ofi_threshold = ofi_threshold
        self.transaction_cost = transaction_cost # 1 bps execution fee/slippage
        self.trades = []
        self.equity_curve = []

    @staticmethod
    def generate_synthetic_lob_data(num_samples=1000):
        """Generates realistic synthetic Level-2 Order Book tick data for backtesting"""
        np.random.seed(42)
        base_price = 85000.0 # BTC/USD base
        
        prices = base_price + np.cumsum(np.random.randn(num_samples) * 2.5)
        spreads = np.random.uniform(0.01, 0.50, num_samples)
        
        bids_vol = np.random.uniform(1.0, 15.0, num_samples)
        asks_vol = np.random.uniform(1.0, 15.0, num_samples)
        
        df = pd.DataFrame({
            'bid_price': prices - (spreads / 2),
            'ask_price': prices + (spreads / 2),
            'bid_vol': bids_vol,
            'ask_vol': asks_vol
        })
        
        # Calculate Micro-Price and OFI
        df['mid_price'] = (df['bid_price'] + df['ask_price']) / 2
        total_vol = df['bid_vol'] + df['ask_vol']
        df['ofi_ratio'] = (df['bid_vol'] - df['ask_vol']) / total_vol
        df['micro_price'] = ((df['bid_vol'] * df['ask_price']) + (df['ask_vol'] * df['bid_price'])) / total_vol
        
        return df

    def run_backtest(self):
        """Executes event-driven backtest across historical tick events"""
        position = 0 # 0: Flat, 1: Long, -1: Short
        entry_price = 0.0
        capital = 100000.0 # $100,000 initial balance
        self.equity_curve.append(capital)

        for i in range(1, len(self.df)):
            current_tick = self.df.iloc[i]
            ofi = current_tick['ofi_ratio']
            
            # Current Liquidity Execution Prices
            bid_price = current_tick['bid_price']
            ask_price = current_tick['ask_price']

            # Entry Signals
            if position == 0:
                if ofi > self.ofi_threshold: # Strong Buy Imbalance
                    position = 1
                    entry_price = ask_price * (1 + self.transaction_cost) # Pay ask + slippage
                elif ofi < -self.ofi_threshold: # Strong Sell Imbalance
                    position = -1
                    entry_price = bid_price * (1 - self.transaction_cost) # Sell at bid - slippage

            # Exit Signals (Mean reversion of OFI)
            elif position == 1 and ofi < 0: # Long Exit
                exit_price = bid_price * (1 - self.transaction_cost)
                pnl = (exit_price - entry_price) / entry_price * capital
                capital += pnl
                self.trades.append({'type': 'LONG', 'pnl': pnl, 'return': pnl / capital})
                position = 0

            elif position == -1 and ofi > 0: # Short Exit
                exit_price = ask_price * (1 + self.transaction_cost)
                pnl = (entry_price - exit_price) / entry_price * capital
                capital += pnl
                self.trades.append({'type': 'SHORT', 'pnl': pnl, 'return': pnl / capital})
                position = 0

            self.equity_curve.append(capital)

        return self.evaluate_performance(capital)

    def evaluate_performance(self, final_capital):
        """Calculates institutional performance metrics"""
        trades_df = pd.DataFrame(self.trades)
        if len(trades_df) == 0:
            print("No trades executed.")
            return

        total_trades = len(trades_df)
        winning_trades = len(trades_df[trades_df['pnl'] > 0])
        win_rate = (winning_trades / total_trades) * 100
        
        total_pnl = final_capital - 100000.0
        returns = pd.Series(self.equity_curve).pct_change().dropna()
        
        # Sharpe Ratio (annualized assumption for tick data)
        sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252 * 24 * 60) if returns.std() != 0 else 0
        
        # Max Drawdown
        equity_series = pd.Series(self.equity_curve)
        peak = equity_series.cummax()
        drawdown = (equity_series - peak) / peak
        max_drawdown = drawdown.min() * 100

        metrics = [
            ["Metric", "Value"],
            ["Initial Capital", "$100,000.00"],
            ["Final Capital", f"${final_capital:,.2f}"],
            ["Total Net P&L", f"${total_pnl:,.2f}"],
            ["Total Trades", total_trades],
            ["Win Rate", f"{win_rate:.2f}%"],
            ["Sharpe Ratio", f"{sharpe_ratio:.2f}"],
            ["Max Drawdown", f"{max_drawdown:.2f}%"]
        ]

        print("\n=== HFT MICROSTRUCTURE BACKTEST PERFORMANCE ===")
        print(tabulate(metrics, headers="firstrow", tablefmt="fancy_grid"))

if __name__ == "__main__":
    print("[INFO] Generating L2 Tick-Level Order Book Data...")
    raw_data = OFIBacktester.generate_synthetic_lob_data(num_samples=2500)
    
    print("[INFO] Initializing Event-Driven OFI Strategy Backtest...")
    backtester = OFIBacktester(raw_data, ofi_threshold=0.30, transaction_cost=0.00005)
    backtester.run_backtest()