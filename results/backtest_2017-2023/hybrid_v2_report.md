# Institutional Hybrid V2 Backtest Report
**Period:** Aug 2017 - Mar 2023
**Strategy:** Institutional Hybrid V2 (Langkah 20)
**Data:** BTCUSDT 1m (Resampled to 1H for signals)

## Performance Summary
| Metric | Value |
| :--- | :--- |
| **Initial Capital** | $10,000.00 |
| **Final Equity** | **$5,397.02** |
| **Total Return** | -46.03% |
| **Total Trades** | 100 |
| **Win Rate** | 16.00% |
| **Winning Trades** | 16 |
| **Losing Trades** | 84 |

## Key Findings
- **High Drawdown**: The strategy suffered a significant drawdown of ~46% over the 6-year period.
- **Low Win Rate**: A 16% win rate suggests the entry conditions (Sweep + Reclaim + Oversold) are not predicting reversals accurately in this timeframe (H1), or the risk/reward ratio is not high enough to compensate.
- **Bullet 2 Effectiveness**: Bullet 2 (Sniper) was triggered frequently but often resulted in losses, suggesting that "catching the knife" in a bear market or after a failed first attempt is risky without stronger confirmation.
- **Trailing Stop**: The "God Tier Trailing" (ATR 3.0) might be too tight or determining "Highest High" from entry immediately exposes the trade to noise.

## Trade Log (Sample)
```text
[2022-10-01 13:00:00] ENTRY BULLET_2 @ 19332.38 -> CLOSED LOSS (-$69.28)
[2022-12-02 18:00:00] ENTRY BULLET_2 @ 16953.93 -> CLOSED LOSS (-$15.56)
[2022-12-06 20:00:00] ENTRY BULLET_2 @ 16989.60 -> CLOSED LOSS (-$70.53)
[2023-02-10 01:00:00] ENTRY BULLET_1 @ 21894.16 -> CLOSED LOSS (-$62.21)
[2023-02-24 19:00:00] ENTRY BULLET_1 @ 23182.27 -> CLOSED LOSS (-$57.31)
```

## Conclusion
The strict implementation of "Institutional Hybrid V2" as defined in `langkah@20.md` has yielded negative results on historical data. The strategy successfully avoided blowing up the account completely (survived 6 years), but cleaner filters or better exit logic is needed to become profitable.
