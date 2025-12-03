#!/bin/bash
# Run Tau2 with vLLM server (assumes vLLM is already running)

MODEL="Qwen/Qwen3-4B-Thinking-2507"
PORT=8000

# Check if server is running
if ! curl -s --max-time 2 http://localhost:$PORT/v1/models > /dev/null 2>&1; then
  echo "❌ Error: vLLM server is not running on port $PORT"
  echo "Please start it first with: ./start_vllm_cluster.sh"
  exit 1
fi

VLLM_URL="http://localhost:$PORT"
echo "✓ vLLM server is accessible"

# Get actual model name from server
ACTUAL_MODEL=$(curl -s $VLLM_URL/v1/models | jq -r '.data[0].id' 2>/dev/null)
if [ -z "$ACTUAL_MODEL" ] || [ "$ACTUAL_MODEL" == "null" ]; then
  echo "⚠ Warning: Could not get model name from server, using: $MODEL"
  ACTUAL_MODEL="$MODEL"
else
  echo "✓ Server reports model: $ACTUAL_MODEL"
fi

# For LiteLLM with OpenAI-compatible APIs, we can use the model name as-is
# The code will automatically prefix with "openai/" if needed
echo "✓ Using model name: $ACTUAL_MODEL"

# Set environment variables
export OPENAI_API_BASE="$VLLM_URL/v1"
export OPENAI_API_KEY="EMPTY"
# Use same model for NL assertions evaluation
export TAU2_LLM_NL_ASSERTIONS="$ACTUAL_MODEL"

# Unset proxy variables to ensure direct connection to localhost
unset http_proxy
unset https_proxy
unset HTTP_PROXY
unset HTTPS_PROXY

echo "Running Tau2 with vLLM..."
echo "Agent LLM: $ACTUAL_MODEL"
echo "User LLM: $ACTUAL_MODEL"
echo ""

# Run Tau2 with all arguments passed through
tau2 run \
  --domain banking \
  --task-ids banking_001 \
  --agent-llm "$ACTUAL_MODEL" \
  --user-llm "$ACTUAL_MODEL" \
  --agent-llm-args '{"temperature": 0.6, "max_tokens": 130000}' \
  --user-llm-args '{"temperature": 0.6, "max_tokens": 130000}' \
  
  "$@"


