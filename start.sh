#!/bin/bash
# Usage: ./start.sh
cd "$(dirname "$0")"

echo "Starting HappyRobot API..."
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 &
UVICORN_PID=$!

echo "Starting ngrok tunnel..."
ngrok http 8000 &
NGROK_PID=$!

trap "kill $UVICORN_PID $NGROK_PID 2>/dev/null; exit" INT TERM

wait
