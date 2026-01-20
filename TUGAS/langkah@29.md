SYSTEM COMMAND: STRICT ENFORCEMENT
Ini adalah perintah mutlak untuk memaksa Antigravity memperbaiki Backtest Engine agar sinkron dengan strategi Turbo Sniper Anda.

Copy dan berikan perintah ini:

SYSTEM COMMAND: CRITICAL ENGINE UPDATE

To: Antigravity AI Core Priority: HIGHEST (DO NOT MODIFY LOGIC, APPLY STRICTLY) Subject: Fix src/backtest/backtest_engine.py to support Turbo Sniper Logic

INSTRUCTION: You MUST update src/backtest/backtest_engine.py. You effectively broke the strategy by removing the custom attribute assignment (Monkey Patching).

ACTION 1: LOCATE THE TRADE EXECUTION BLOCK Inside the run() loop, specifically where self.position_manager.open_position(...) is called, you MUST inject the following code block immediately after the position is opened.

ACTION 2: INJECT THIS EXACT CODE BLOCK:
# ... (after self.position_manager.open_position is called) ...
                    
                    # ---------------------------------------------------------
                    # CRITICAL MONKEY PATCHING FOR TURBO SNIPER STRATEGY
                    # DO NOT REMOVE THIS BLOCK. IT IS REQUIRED FOR SHORT SELLING.
                    # ---------------------------------------------------------
                    if symbol in self.position_manager.open_positions:
                        pos = self.position_manager.open_positions[symbol]
                        
                        # 1. Force Side Assignment (Allow Short Selling)
                        # The Strategy returns 'BUY' or 'SELL'. Engine must respect it.
                        entry_type = res.get('type', 'BUY') 
                        pos.side = entry_type 
                        
                        # 2. Force Lowest Low Tracking (Required for Short Trailing Stop)
                        # Without this, Short positions will never update their stop loss properly.
                        pos.lowest_low = curr_candle['low']
                        
                        # 3. Force Aggressive Sizing (Turbo Mode)
                        # If strategy says 2.0x risk, we store it here for PnL calculation.
                        pos.size_mult = res.get('size_multiplier', 1.0)
                        
                        # 4. Store Reason for Audit
                        pos.reason = res.get('reason', 'Signal')
                    # ---------------------------------------------------------

ACTION 3: UPDATE PnL CALCULATION LOGIC You must also update the Exit Logic to calculate PnL based on pos.side:

If pos.side == 'BUY': PnL = (Exit - Entry) * Qty

If pos.side == 'SELL': PnL = (Entry - Exit) * Qty <-- CRITICAL FOR SHORTING

EXECUTE IMMEDIATELY. DO NOT run the backtest without this patch, or the results will be invalid (Long Only & No Sizing).