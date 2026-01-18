from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import random

class SentimentMaster:
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()
        # Threshold untuk HYPE Mode sesuai Blueprint
        self.hype_threshold = 0.5 

    def get_mock_news(self):
        """
        Simulasi mengambil berita terkini.
        Nanti bisa diganti dengan real RSS Feed dari Coindesk/Cointelegraph.
        """
        scenarios = [
            # Skenario Bullish
            [
                "Bitcoin breaks $100k barrier as institutions rush in",
                "SEC approves new Crypto ETF, market soars",
                "Michael Saylor buys more Bitcoin",
                "Inflation drops, Fed hints at rate cuts"
            ],
            # Skenario Bearish
            [
                "Exchange hacked, thousands of Bitcoin stolen",
                "Government announces strict ban on crypto trading",
                "Bitcoin crashes below support levels",
                "Market fear rises as recession looms"
            ],
            # Skenario Netral/Mixed
            [
                "Bitcoin consolidates around $50k",
                "Top 10 altcoins to watch this week",
                "Crypto market shows mixed signals",
                "Analyst predicts sideways movement"
            ]
        ]
        return random.choice(scenarios)

    def analyze(self, headlines=None):
        """
        Input: List of strings (headlines). Jika None, pakai data mock.
        Output: Dict {score, signal, mode}
        """
        if not headlines:
            headlines = self.get_mock_news()

        total_score = 0
        details = []
        
        print(f"\n📰 ANALYZING {len(headlines)} HEADLINES:")
        
        for news in headlines:
            # VADER menghasilkan compound score (-1 s/d 1)
            vs = self.analyzer.polarity_scores(news)
            score = vs['compound']
            total_score += score
            details.append(f"   Score {score:.2f}: {news[:50]}...")
            print(f"   > {news[:50]}... ({score:.2f})")

        # Rata-rata sentimen
        avg_score = total_score / len(headlines) if headlines else 0
        
        # Tentukan Mode sesuai Blueprint
        mode = "NORMAL"
        if avg_score >= 0.2: # Agak longgar dikit untuk demo
            mode = "HYPE (Greed)"
        elif avg_score <= -0.2:
            mode = "FEAR (Panic)"
        
        return {
            'average_score': avg_score,
            'mode': mode,
            'headlines': headlines,
            'details': details
        }
