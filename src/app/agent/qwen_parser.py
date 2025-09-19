"""
Qwen Tool Call Parser for Kani

This module provides a custom tool call parser for Qwen models that use XML-based
function calling format with <tool_call> tags.
"""

import json
import logging
import re
from typing import Any, AsyncGenerator, List, Tuple

from kani.engines.base import BaseCompletion
from kani.model_specific.base import BaseToolCallParser
from kani.models import FunctionCall, ToolCall

log = logging.getLogger(__name__)


class QwenToolCallParser(BaseToolCallParser):  # type: ignore[misc]
    """
    Tool calling parser for Qwen models that use XML-based function calling.

    Qwen models output function calls in the format:
    <tool_call>
    {"name": "function_name", "arguments": {...}}
    </tool_call>
    """

    def __init__(
        self,
        *args: Any,
        tool_call_start_token: str = "<tool_call>",
        tool_call_end_token: str = "</tool_call>",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            *args,
            tool_call_start_token=tool_call_start_token,
            tool_call_end_token=tool_call_end_token,
            **kwargs,
        )

    def parse_tool_calls(self, content: str) -> Tuple[str, List[ToolCall]]:
        """
        Parse tool calls from Qwen's XML format.

        Args:
            content: The raw content from the model

        Returns:
            Tuple of (cleaned_content, list_of_tool_calls)
        """
        if not isinstance(content, str):
            return str(content), []

        # Ensure tokens are strings
        start_token = self.tool_call_start_token or "<tool_call>"
        end_token = self.tool_call_end_token or "</tool_call>"

        # Look for tool calls in XML format
        tool_call_pattern = (
            rf"{re.escape(start_token)}\s*(.+?)\s*{re.escape(end_token)}"
        )

        tool_calls = []
        cleaned_content = content

        # Find all tool calls
        for match in re.finditer(tool_call_pattern, content, re.IGNORECASE | re.DOTALL):
            tool_json_str = match.group(1).strip()
            log.debug(f"Found tool call JSON: {tool_json_str}")

            try:
                # Parse the JSON content
                tool_data = json.loads(tool_json_str)

                # Extract function details
                function_name = tool_data.get("name")
                function_args = tool_data.get("arguments", {})

                if function_name:
                    # Create function call
                    function_call = FunctionCall(
                        name=function_name,
                        arguments=json.dumps(function_args)
                        if isinstance(function_args, dict)
                        else str(function_args),
                    )

                    # Create tool call (Kani expects this format)
                    tool_call = ToolCall.from_function_call(function_call)
                    tool_calls.append(tool_call)

                    log.debug(
                        f"Parsed tool call: {function_name} with args: {function_args}"
                    )

            except json.JSONDecodeError as e:
                log.warning(
                    f"Failed to parse tool call JSON: {tool_json_str}, error: {e}"
                )
                continue

        # Remove tool call XML from content if we found any
        if tool_calls:
            cleaned_content = re.sub(
                tool_call_pattern, "", content, flags=re.IGNORECASE | re.DOTALL
            ).strip()

        return cleaned_content, tool_calls

    async def predict(
        self, messages: Any, functions: Any = None, **hyperparams: Any
    ) -> Any:
        """Override predict to handle tool call parsing."""
        completion = await super().predict(messages, functions, **hyperparams)

        # Parse and clean the content
        content = completion.message.content
        if isinstance(content, str):
            cleaned_content, tool_calls = self.parse_tool_calls(content)
            completion.message.content = cleaned_content
            if tool_calls:
                completion.message.tool_calls = tool_calls

        return completion

    async def stream(
        self, messages: Any, functions: Any = None, **hyperparams: Any
    ) -> AsyncGenerator[Any, None]:
        """Override stream to handle tool call parsing."""
        # Note: Streaming with tool calls is more complex - for now, just handle basic case
        async for elem in super().stream(messages, functions, **hyperparams):
            if isinstance(elem, BaseCompletion) and hasattr(elem, "message"):
                content = elem.message.content
                if isinstance(content, str):
                    # Parse and clean content for final message
                    cleaned_content, tool_calls = self.parse_tool_calls(content)
                    elem.message.content = cleaned_content
                    if tool_calls:
                        elem.message.tool_calls = tool_calls
            yield elem
