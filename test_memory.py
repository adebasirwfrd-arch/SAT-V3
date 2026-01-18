from src.utils.state_manager import StateManager
import time
import os

def run_test():
    print("🧠 TESTING ELEPHANT MEMORY (State Persistence)...\n")
    
    # Hapus memory lama biar bersih
    if os.path.exists('data/memory.json'):
        os.remove('data/memory.json')

    # 1. Bot Hidup & Beli
    print("🤖 [SESSION 1] Bot Starting...")
    brain = StateManager()
    print(f"   Initial Status: {brain.state['status']}")
    
    dummy_trade = {
        'symbol': 'BTC/USDT',
        'entry_price': 50000,
        'quantity': 0.1,
        'stop_loss': 49000,
        'take_profit': 52000,
        'order_id': '882910'
    }
    
    print("   >>> BUY EXECUTED!")
    brain.update_position(dummy_trade)
    
    # 2. Simulasi Mati Lampu (Kill Object)
    print("\n💥 [CRASH] System going down... (Deleting object)")
    del brain
    
    # 3. Bot Hidup Lagi (Restart)
    print("\n🤖 [SESSION 2] Bot Restarting (Rebooting)...")
    new_brain = StateManager() # Load file json yg tadi disimpan
    
    current_status = new_brain.state['status']
    saved_symbol = new_brain.state['current_position']['symbol']
    saved_price = new_brain.state['current_position']['entry_price']
    
    print(f"   Restored Status: {current_status}")
    print(f"   Restored Position: {saved_symbol} @ ${saved_price}")
    
    # 4. Validasi
    if current_status == "IN_POSITION" and saved_price == 50000:
        print("\n✅ TEST PASSED: Bot remembers position after restart.")
    else:
        print("\n❌ TEST FAILED: Bot suffered amnesia.")

if __name__ == "__main__":
    run_test()
