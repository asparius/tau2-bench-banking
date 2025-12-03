#!/bin/bash
# Stop vLLM server

PID_FILE="vllm_server.pid"

if [ ! -f "$PID_FILE" ]; then
  echo "PID file not found. Server may not be running."
  exit 1
fi

PID=$(cat "$PID_FILE")

if ps -p $PID > /dev/null 2>&1; then
  echo "Stopping vLLM server (PID: $PID)..."
  kill $PID
  rm "$PID_FILE"
  echo "Server stopped."
else
  echo "Process $PID not found. Cleaning up PID file."
  rm "$PID_FILE"
fi


