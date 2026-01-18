import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    PROJECT_NAME = "SAT-V3 Magnificent 7"
    VERSION = "2.0.0"  # Multi-Crypto Edition
    
    # Trading Settings - 6 Crypto Pairs
    TRADING_PAIRS = [
        'BTC/USDT',
        'ETH/USDT',
        'SOL/USDT',
        'BNB/USDT',
        'TON/USDT',
        'XRP/USDT'
    ]
    
    SYMBOL = 'BTC/USDT'  # Default/Primary
    TIMEFRAME = '1h'
    
    # Portfolio Settings
    INITIAL_CAPITAL = 10000.0
    MAX_POSITION_SIZE = 0.15  # 15% per coin
    MAX_TOTAL_EXPOSURE = 0.60  # 60% max invested
    
    # Path Settings
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    LOG_DIR = os.path.join(BASE_DIR, 'logs')
    
    # Binance Config
    API_KEY = os.getenv("BINANCE_API_KEY")
    SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")
    SANDBOX = True  # Testnet mode
    
    # Data Files
    LIVE_DATA_FILE = os.path.join(DATA_DIR, 'multi_asset_data.json')
    WALLET_FILE = os.path.join(DATA_DIR, 'wallet.json')
    COMMANDS_FILE = os.path.join(DATA_DIR, 'commands.json')
    TRADES_FILE = os.path.join(DATA_DIR, 'trades.csv')
