#!/bin/bash

echo "🍏 STARTING SAT-V3 (Local MacBook Mode)..."
echo "☕ Activating Caffeine (Preventing Sleep)..."

# 1. Activate Venv
source venv/bin/activate

# 2. Launch Dashboard (Background)
echo "📊 Launching Dashboard..."
streamlit run src/dashboard/app.py --server.port 8501 --server.headless true > logs/dashboard.log 2>&1 &
DASHBOARD_PID=$!

# 3. Launch Bot dengan Caffeinate
# -i: Prevent idle sleep (layar boleh mati, sistem tidak)
# -s: Prevent system sleep (saat dicolok power)
echo "🤖 Launching Engine (Press Ctrl+C to Stop)..."
caffeinate -i -s python src/main.py

# 4. Cleanup
kill $DASHBOARD_PID
echo "👋 Bye!"
