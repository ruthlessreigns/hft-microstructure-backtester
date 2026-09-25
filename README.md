# HFT Microstructure & Order Flow Imbalance (OFI) Backtester

A high-performance, tick-by-tick event-driven market microstructure backtesting engine designed for high-frequency trading (HFT) and market-making quantitative strategies.

## Key Features

- **Event-Driven Architecture:** Simulates real-time order book state changes at tick precision.
- **Order Flow Imbalance (OFI) Metrics:** Computes real-time liquidity imbalance between bid and ask volumes.
- **Micro-Price Modeling:** Incorporates volume-weighted micro-price calculations to anticipate short-term direction.
- **Institutional Cost Modeling:** Realistic slippage, bid-ask spread costs, and exchange fee execution simulation.
- **Performance Analytics:** Automated calculation of Sharpe Ratio, Max Drawdown, Win Rate, and Net P&L.

## Mathematical Formulation

Order Flow Imbalance (OFI) Ratio is computed as:

$$OFI_{ratio} = \frac{V_{bid} - V_{ask}}{V_{bid} + V_{ask}}$$

Micro-Price is derived using volume weighting across top-of-book levels:

$$P_{micro} = \frac{V_{bid} \cdot P_{ask} + V_{ask} \cdot P_{bid}}{V_{bid} + V_{ask}}$$

## Getting Started

1. Clone the repository:
   ```bash
   git clone [https://github.com/ruthlessreigns/hft-microstructure-backtester.git](https://github.com/ruthlessreigns/hft-microstructure-backtester.git)
   cd hft-microstructure-backtester