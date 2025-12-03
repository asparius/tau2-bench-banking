#!/bin/bash
# Start vLLM server in background for cluster environment

MODEL="Qwen/Qwen3-4B-Thinking-2507"
PORT=8000
LOG_FILE="vllm_server.log"
PID_FILE="vllm_server.pid"


echo "Starting vLLM server with model: $MODEL"
echo "Port: $PORT"
echo "Log file: $LOG_FILE"

# Start vLLM in background using vllm serve
# Note: --enable-auto-tool-choice and --tool-call-parser are needed for "auto" tool choice
# But we'll use "required" in code instead, which works without these flags
nohup vllm serve "$MODEL" \
  --port $PORT \
  --host 0.0.0.0 \
  --trust-remote-code \
  --tensor_parallel_size 2 \
  --reasoning-parser deepseek_r1 \
  --tool-call-parser qwen3_xml \
  --enable_auto_tool_choice \
  --max-model-len 220000 \
  --gpu-memory-utilization 0.9 \
  > "$LOG_FILE" 2>&1 &

# Save PID
echo $! > "$PID_FILE"
echo "vLLM server started with PID: $(cat $PID_FILE)"
echo "Logs are being written to: $LOG_FILE"
echo ""
echo "Waiting for server to start..."

# Wait for server to be ready (max 180 seconds - models can take time to load)
# Bypass proxy for localhost connections
echo "Waiting for server to be ready (this can take 2-3 minutes for model loading)..."
for i in {1..180}; do
  if curl -s --max-time 2 http://localhost:$PORT/v1/models > /dev/null 2>&1; then
    echo "✓ Server is ready! (took $i seconds)"
    echo ""
    echo "Model name from server:"
    MODEL_NAME=$(curl -s http://localhost:$PORT/v1/models | jq -r '.data[0].id' 2>/dev/null)
    if [ -n "$MODEL_NAME" ] && [ "$MODEL_NAME" != "null" ]; then
      echo "  $MODEL_NAME"
    else
      curl -s http://localhost:$PORT/v1/models | grep -o '"id":"[^"]*"' | head -1
    fi
    echo ""
    echo "To stop the server, run: kill $(cat $PID_FILE)"
    echo "Or use: ./stop_vllm.sh"
    echo ""
    echo "To test connection, run: ./test_vllm_connection.sh"
    exit 0
  fi
  sleep 1
  if [ $((i % 30)) -eq 0 ]; then
    echo "Still waiting... ($i seconds) - Model loading can take 2-3 minutes"
    # Check if process is still running
    if ! ps -p $(cat $PID_FILE) > /dev/null 2>&1; then
      echo "❌ Server process died! Check $LOG_FILE for errors."
      exit 1
    fi
  fi
done

echo "⚠ Warning: Server may not be ready yet after 180 seconds."
echo "Check $LOG_FILE for details. The server might still be loading."
echo ""
echo "You can manually test with:"
echo "  curl http://localhost:$PORT/v1/models"
echo "Or run: ./test_vllm_connection.sh"


