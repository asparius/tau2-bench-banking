import json
import os
import re
from typing import Any, Optional

import litellm
from litellm import completion, completion_cost
from litellm.caching.caching import Cache
from litellm.main import ModelResponse, Usage
from loguru import logger

from tau2.config import (
    DEFAULT_LLM_CACHE_TYPE,
    DEFAULT_MAX_RETRIES,
    LLM_CACHE_ENABLED,
    REDIS_CACHE_TTL,
    REDIS_CACHE_VERSION,
    REDIS_HOST,
    REDIS_PASSWORD,
    REDIS_PORT,
    REDIS_PREFIX,
    USE_LANGFUSE,
)
from tau2.data_model.message import (
    AssistantMessage,
    Message,
    SystemMessage,
    ToolCall,
    ToolMessage,
    UserMessage,
)
from tau2.environment.tool import Tool

# litellm._turn_on_debug()

if USE_LANGFUSE:
    # set callbacks
    litellm.success_callback = ["langfuse"]
    litellm.failure_callback = ["langfuse"]

litellm.drop_params = True

if LLM_CACHE_ENABLED:
    if DEFAULT_LLM_CACHE_TYPE == "redis":
        logger.info(f"LiteLLM: Using Redis cache at {REDIS_HOST}:{REDIS_PORT}")
        litellm.cache = Cache(
            type=DEFAULT_LLM_CACHE_TYPE,
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            namespace=f"{REDIS_PREFIX}:{REDIS_CACHE_VERSION}:litellm",
            ttl=REDIS_CACHE_TTL,
        )
    elif DEFAULT_LLM_CACHE_TYPE == "local":
        logger.info("LiteLLM: Using local cache")
        litellm.cache = Cache(
            type="local",
            ttl=REDIS_CACHE_TTL,
        )
    else:
        raise ValueError(
            f"Invalid cache type: {DEFAULT_LLM_CACHE_TYPE}. Should be 'redis' or 'local'"
        )
    litellm.enable_cache()
else:
    logger.info("LiteLLM: Cache is disabled")
    litellm.disable_cache()


ALLOW_SONNET_THINKING = False

if not ALLOW_SONNET_THINKING:
    logger.warning("Sonnet thinking is disabled")


def _parse_ft_model_name(model: str) -> str:
    """
    Parse the ft model name from the litellm model name.
    e.g: "ft:gpt-4.1-mini-2025-04-14:sierra::BSQA2TFg" -> "gpt-4.1-mini-2025-04-14"
    """
    pattern = r"ft:(?P<model>[^:]+):(?P<provider>\w+)::(?P<id>\w+)"
    match = re.match(pattern, model)
    if match:
        return match.group("model")
    else:
        return model


def get_response_cost(response: ModelResponse) -> float:
    """
    Get the cost of the response from the litellm completion.
    """
    response.model = _parse_ft_model_name(
        response.model
    )  # FIXME: Check Litellm, passing the model to completion_cost doesn't work.
    try:
        cost = completion_cost(completion_response=response)
    except Exception as e:
        # For local models, cost calculation often fails - that's fine, return 0.0
        # Only log as warning, not error, since this is expected for unmapped models
        if "isn't mapped yet" in str(e) or "model_prices" in str(e):
            logger.debug(f"Model not in pricing database (local model?): {e}")
        else:
            logger.warning(f"Could not calculate cost: {e}")
        return 0.0
    return cost


def get_response_usage(response: ModelResponse) -> Optional[dict]:
    usage: Optional[Usage] = response.get("usage")
    if usage is None:
        return None
    return {
        "completion_tokens": usage.completion_tokens,
        "prompt_tokens": usage.prompt_tokens,
    }


def to_tau2_messages(
    messages: list[dict], ignore_roles: set[str] = set()
) -> list[Message]:
    """
    Convert a list of messages from a dictionary to a list of Tau2 messages.
    """
    tau2_messages = []
    for message in messages:
        role = message["role"]
        if role in ignore_roles:
            continue
        if role == "user":
            tau2_messages.append(UserMessage(**message))
        elif role == "assistant":
            tau2_messages.append(AssistantMessage(**message))
        elif role == "tool":
            tau2_messages.append(ToolMessage(**message))
        elif role == "system":
            tau2_messages.append(SystemMessage(**message))
        else:
            raise ValueError(f"Unknown message type: {role}")
    return tau2_messages


def to_litellm_messages(messages: list[Message]) -> list[dict]:
    """
    Convert a list of Tau2 messages to a list of litellm messages.
    """
    litellm_messages = []
    for message in messages:
        if isinstance(message, UserMessage):
            litellm_messages.append({"role": "user", "content": message.content})
        elif isinstance(message, AssistantMessage):
            tool_calls = None
            if message.is_tool_call():
                tool_calls = [
                    {
                        "id": tc.id,
                        "name": tc.name,
                        "function": {
                            "name": tc.name,
                            "arguments": json.dumps(tc.arguments),
                        },
                        "type": "function",
                    }
                    for tc in message.tool_calls
                ]
            litellm_messages.append(
                {
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": tool_calls,
                }
            )
        elif isinstance(message, ToolMessage):
            litellm_messages.append(
                {
                    "role": "tool",
                    "content": message.content,
                    "tool_call_id": message.id,
                }
            )
        elif isinstance(message, SystemMessage):
            litellm_messages.append({"role": "system", "content": message.content})
    return litellm_messages


def parse_json_wrapped_content(content: str) -> str:
    """
    Parse JSON-wrapped content from vLLM (e.g., {"type": "message", "content": "..."} or {"message": "..."}).
    Returns the extracted content string.
    """
    if not content or not content.strip().startswith("{"):
        return content
    
    try:
        # Try to parse as JSON
        parsed = json.loads(content.strip())
        if isinstance(parsed, dict):
            # Try "content" key first (OpenAI format)
            if "content" in parsed:
                return parsed["content"]
            # Try "message" key (vLLM qwen3_xml format)
            if "message" in parsed:
                return parsed["message"]
            # If it's a dict with "type": "message", extract content
            if parsed.get("type") == "message" and "content" in parsed:
                return parsed["content"]
    except json.JSONDecodeError:
        # Not valid JSON, return as-is
        pass
    
    return content


def parse_xml_tool_calls(content: str) -> tuple[str, list[ToolCall]]:
    """
    Parse XML-formatted tool calls from content (e.g., from vLLM with qwen3_xml parser).
    Returns (cleaned_content, tool_calls).
    """
    tool_calls = []
    # Pattern to match <tool_call>...</tool_call> blocks
    pattern = r'<tool_call>\s*(.*?)\s*</tool_call>'
    matches = re.findall(pattern, content, re.DOTALL)
    
    for match in matches:
        try:
            # Parse the JSON inside the tool_call tags
            tool_data = json.loads(match.strip())
            if isinstance(tool_data, dict) and "name" in tool_data:
                tool_calls.append(
                    ToolCall(
                        id=f"call_{len(tool_calls)}",  # Generate a simple ID
                        name=tool_data["name"],
                        arguments=tool_data.get("arguments", {}),
                    )
                )
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse tool call JSON: {match[:100]}")
            continue
    
    # Remove tool_call XML tags from content
    cleaned_content = re.sub(pattern, '', content, flags=re.DOTALL).strip()
    
    return cleaned_content, tool_calls


def generate(
    model: str,
    messages: list[Message],
    tools: Optional[list[Tool]] = None,
    tool_choice: Optional[str] = None,
    **kwargs: Any,
) -> UserMessage | AssistantMessage:
    """
    Generate a response from the model.

    Args:
        model: The model to use.
        messages: The messages to send to the model.
        tools: The tools to use.
        tool_choice: The tool choice to use.
        **kwargs: Additional arguments to pass to the model.

    Returns: A tuple containing the message and the cost.
    """
    if kwargs.get("num_retries") is None:
        kwargs["num_retries"] = DEFAULT_MAX_RETRIES

    if model.startswith("claude") and not ALLOW_SONNET_THINKING:
        kwargs["thinking"] = {"type": "disabled"}
    
    # Handle OpenAI-compatible local servers (e.g., vLLM)
    # If OPENAI_API_BASE is set, explicitly pass api_base to LiteLLM
    openai_api_base = os.environ.get("OPENAI_API_BASE")
    is_local_server = False
    if openai_api_base and "api_base" not in kwargs:
        kwargs["api_base"] = openai_api_base
        is_local_server = "localhost" in openai_api_base or "127.0.0.1" in openai_api_base
        # For OpenAI-compatible endpoints, LiteLLM needs to know it's an OpenAI provider
        # If model name doesn't match OpenAI patterns, prefix with "openai/" to force provider detection
        # LiteLLM will strip the "openai/" prefix when sending to the server
        if not any(model.startswith(prefix) for prefix in ("openai/", "gpt-", "o1-", "o3-", "text-", "davinci", "curie", "babbage", "ada")):
            # Use "openai/" prefix to tell LiteLLM this is an OpenAI-compatible endpoint
            # LiteLLM will send the model name (without prefix) to the custom api_base
            model = f"openai/{model}"
            logger.debug(f"Using OpenAI-compatible endpoint. Model: {model}, API Base: {openai_api_base}")
    
    litellm_messages = to_litellm_messages(messages)
    tools = [tool.openai_schema for tool in tools] if tools else None
    # For vLLM with reasoning models and qwen3_xml parser, tool calling can be tricky
    # Don't set tool_choice - let the model decide naturally
    # The qwen3_xml parser will handle XML-formatted tool calls if the model chooses to use them
    if tools and tool_choice is None:
        # For local servers with reasoning, don't force tool_choice
        # Let the model naturally decide whether to use tools or respond with text
        if is_local_server:
            tool_choice = None  # Don't set tool_choice - let model decide
        else:
            tool_choice = "auto"
    try:
        # Only pass tool_choice if it's explicitly set (not None)
        completion_kwargs = {"model": model, "messages": litellm_messages, **kwargs}
        if tools:
            completion_kwargs["tools"] = tools
        if tool_choice is not None:
            completion_kwargs["tool_choice"] = tool_choice
        
        response = completion(**completion_kwargs)
    except Exception as e:
        logger.error(e)
        raise e
    cost = get_response_cost(response)
    usage = get_response_usage(response)
    response = response.choices[0]
    try:
        finish_reason = response.finish_reason
        if finish_reason == "length":
            logger.warning("Output might be incomplete due to token limit!")
    except Exception as e:
        logger.error(e)
        raise e
    assert response.message.role == "assistant", (
        "The response should be an assistant message"
    )
    
    # Handle reasoning models (vLLM with --enable-reasoning)
    # vLLM returns both reasoning_content (thinking) and content (final answer)
    # We use content (final answer) for the actual response
    content = response.message.content
    reasoning_content = getattr(response.message, 'reasoning_content', None)
    
    # Log reasoning if present (for debugging)
    if reasoning_content:
        logger.debug(f"Reasoning content: {reasoning_content[:200]}...")
    
    # Parse JSON-wrapped content (vLLM with qwen3_xml may return {"type": "message", "content": "..."})
    if content:
        content = parse_json_wrapped_content(content)
    
    # First, try to get structured tool_calls from the response
    tool_calls = response.message.tool_calls or []
    tool_calls = [
        ToolCall(
            id=tool_call.id,
            name=tool_call.function.name,
            arguments=json.loads(tool_call.function.arguments),
        )
        for tool_call in tool_calls
    ]
    
    # If no structured tool_calls but content contains XML tool calls (vLLM with qwen3_xml),
    # parse them from the content
    if not tool_calls and content and "<tool_call>" in content:
        cleaned_content, xml_tool_calls = parse_xml_tool_calls(content)
        if xml_tool_calls:
            content = cleaned_content
            tool_calls = xml_tool_calls
            logger.debug(f"Parsed {len(xml_tool_calls)} tool calls from XML content")
    
    tool_calls = tool_calls or None

    message = AssistantMessage(
        role="assistant",
        content=content,
        tool_calls=tool_calls,
        cost=cost,
        usage=usage,
        raw_data=response.to_dict(),
    )
    return message


def get_cost(messages: list[Message]) -> tuple[float, float] | None:
    """
    Get the cost of the interaction between the agent and the user.
    Returns None if any message has no cost.
    """
    agent_cost = 0
    user_cost = 0
    for message in messages:
        if isinstance(message, ToolMessage):
            continue
        if message.cost is not None:
            if isinstance(message, AssistantMessage):
                agent_cost += message.cost
            elif isinstance(message, UserMessage):
                user_cost += message.cost
        else:
            logger.warning(f"Message {message.role}: {message.content} has no cost")
            return None
    return agent_cost, user_cost


def get_token_usage(messages: list[Message]) -> dict:
    """
    Get the token usage of the interaction between the agent and the user.
    """
    usage = {"completion_tokens": 0, "prompt_tokens": 0}
    for message in messages:
        if isinstance(message, ToolMessage):
            continue
        if message.usage is None:
            logger.warning(f"Message {message.role}: {message.content} has no usage")
            continue
        usage["completion_tokens"] += message.usage["completion_tokens"]
        usage["prompt_tokens"] += message.usage["prompt_tokens"]
    return usage

