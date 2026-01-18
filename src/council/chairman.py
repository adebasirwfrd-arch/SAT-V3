import pandas as pd
from .trend_master import TrendMaster
from .structure_master import StructureMaster
from .volume_master import VolumeMaster
from .indicator_master import IndicatorMaster
from .smart_money_master import SmartMoneyMaster
from .pattern_master import PatternMaster
from .geometry_master import GeometryMaster
from .sentiment_master import SentimentMaster

class TheChairman:
    def __init__(self):
        self.generals = [
            TrendMaster(),
            StructureMaster(),
            VolumeMaster(),
            IndicatorMaster(),
            SmartMoneyMaster(),
            PatternMaster(),
            GeometryMaster()
        ]
        self.sentiment_bot = SentimentMaster()

    def solicit_votes(self, df: pd.DataFrame) -> dict:
        # 1. Cek Sentimen Dulu (Divisi 2)
        sentiment_result = self.sentiment_bot.analyze()
        market_mood = sentiment_result['mode']
        sentiment_score = sentiment_result['average_score']
        
        print(f"\n🌐 MARKET MOOD: {market_mood} (Score: {sentiment_score:.2f})")
        
        # 2. Tentukan Ambang Batas (Threshold) berdasarkan Blueprint
        # Normal: > 70 untuk BUY
        # Hype: > 50 untuk BUY (Lebih Agresif)
        buy_threshold = 70
        if "HYPE" in market_mood:
            buy_threshold = 50
            print("⚠️ HYPE DETECTED: Lowering Buy Threshold to 50 (Aggressive Mode)")

        # 3. Lakukan Voting 7 Jenderal (Divisi 1)
        total_score = 0
        total_weight = 0
        details = {}
        
        print("\n--- 🗳️ COUNCIL VOTING SESSION ---")
        for general in self.generals:
            vote = general.analyze(df)
            weighted_s = vote['score'] * general.weight
            total_score += weighted_s
            total_weight += general.weight
            details[general.name] = vote
            print(f"👤 {general.name}: {vote['signal']} ({vote['score']})")

        final_score = total_score / total_weight if total_weight > 0 else 50
        
        # 4. Final Verdict dengan Threshold Dinamis
        final_signal = "NEUTRAL"
        
        if final_score >= buy_threshold:
            final_signal = "STRONG BUY" if final_score >= 80 else "BUY"
        elif final_score <= 30: 
            final_signal = "STRONG SELL"
        elif final_score <= 40: 
            final_signal = "SELL"
        
        print(f"--- ⚖️ FINAL VERDICT: {final_signal} (Score: {final_score:.2f} | Threshold: {buy_threshold}) ---\n")
        
        return {
            'final_score': final_score,
            'final_signal': final_signal,
            'sentiment': sentiment_result,
            'details': details
        }
