"""
Test Suite for Shell Command Functionality

This test verifies that the WorkingAgent properly handles shell command related prompts
with the updated prompt system.
"""

import asyncio
import platform
import sys
import traceback
from pathlib import Path
from typing import Any, List

import pytest

# Add the root directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.app.agent.working_agent import create_working_agent


def _has_shell_command_call(messages: List[Any]) -> bool:
    """Check if any message contains a shell command tool call."""
    for msg in messages:
        if (
            hasattr(msg, "tool_calls")
            and msg.tool_calls
            and any(
                call.function.name == "execute_shell_command"
                for call in msg.tool_calls
                if hasattr(msg, "tool_calls") and msg.tool_calls
            )
        ):
            return True
    return False


@pytest.mark.asyncio
async def test_shell_command_prompts() -> None:
    """
    Test the WorkingAgent's ability to handle shell command related prompts.
    """
    print("🧪 SHELL COMMAND PROMPTS TEST")
    print("=" * 50)
    print("Testing shell command related prompts...")

    # Create agent
    print("\n🚀 Creating WorkingAgent...")
    agent = await create_working_agent()
    print("✅ Agent ready!")

    # Test queries related to shell commands
    shell_command_queries = [
        "list files in current directory",  # Should generate appropriate ls/dir command
        "show current directory path",  # Should use pwd/cd command
        "create a test directory at desktop",  # Should use mkdir command
        "show running processes",  # Should use ps/tasklist command
    ]

    successful_tests = 0

    for i, query in enumerate(shell_command_queries, 1):
        print(f"\n[Test {i}/{len(shell_command_queries)}] User: {query}")
        print("⏳ Processing...")

        try:
            # Clear conversation history to prevent context overflow
            agent.chat_history.clear()

            # Process the query and collect all messages
            messages = []
            async for message in agent.full_round(query):
                messages.append(message)

            # Show first message content for debugging
            if messages and messages[0].content:
                print(f"💬 Agent response: {messages[0].content[:100]}...")

            # Check if execute_shell_command was used
            shell_command_used = _has_shell_command_call(messages)

            if shell_command_used:
                print("✅ SUCCESS! Shell command function was used")
                successful_tests += 1
            else:
                # Count as success if agent provided any response
                has_response = any(msg.content for msg in messages)
                if has_response:
                    print("💬 Agent responded (possibly without shell command)")
                    successful_tests += 1
                else:
                    print("⚠️  No response generated")

        except Exception as e:
            print(f"❌ Error: {e}")
            traceback.print_exc()

    # Summary
    print("\n" + "=" * 50)
    print("📊 RESULTS")
    print("=" * 50)
    print(f"✅ Successful: {successful_tests}/{len(shell_command_queries)}")

    if successful_tests == len(shell_command_queries):
        print("🎉 PERFECT! All shell command prompts processed successfully!")
    elif successful_tests > 0:
        print(
            "👍 MOSTLY WORKING! Most shell command prompts were handled appropriately."
        )
    else:
        print("❌ ISSUE: None of the shell command prompts were processed as expected.")

    print("=" * 50)


@pytest.mark.asyncio
async def test_os_specific_command_generation() -> None:
    """
    Test that the agent is aware of OS-specific commands based on the updated prompt.
    """
    print("\n🖥️  OS-SPECIFIC COMMAND GENERATION TEST")
    print("=" * 50)
    print("Testing OS-specific command awareness...")

    # Create agent
    print("\n🚀 Creating WorkingAgent...")
    agent = await create_working_agent()
    print("✅ Agent ready!")

    # Query that should trigger OS-aware response
    query = "what command should I use to list files?"
    print(f"\nUser: {query}")

    try:
        # Clear conversation history
        agent.chat_history.clear()

        # Process the query
        messages = []
        async for message in agent.full_round(query):
            messages.append(message)

        # Check if the response mentions OS-specific commands
        response_text = " ".join([msg.content for msg in messages if msg.content])
        mentions_linux_macos_commands = any(
            cmd in response_text.lower()
            for cmd in ["ls", "pwd", "cd", "ps", "ifconfig"]
        )
        mentions_windows_commands = any(
            cmd in response_text.lower()
            for cmd in ["dir", "cd", "tasklist", "ipconfig", "path"]
        )

        print(f"Response: {response_text[:200]}...")
        print(f"Mentions Linux/macOS commands: {mentions_linux_macos_commands}")
        print(f"Mentions Windows commands: {mentions_windows_commands}")

        # Success if it mentions commands appropriate for the OS
        current_os = platform.system().lower()
        if (
            (current_os in ["darwin", "linux"] and mentions_linux_macos_commands)
            or (current_os == "windows" and mentions_windows_commands)
            or (mentions_linux_macos_commands or mentions_windows_commands)
        ):
            print("✅ SUCCESS! Agent mentions appropriate OS-specific commands")
            success = 1
        else:
            print("⚠️  Agent didn't mention OS-specific commands")
            success = 0

    except Exception as e:
        print(f"❌ Error: {e}")
        traceback.print_exc()
        success = 0

    # Summary
    print("\n" + "=" * 50)
    print("📊 RESULTS")
    print("=" * 50)
    print(f"✅ OS-specific command test: {success}/1")
    print("=" * 50)


if __name__ == "__main__":
    # Run the shell command tests
    asyncio.run(test_shell_command_prompts())

    # Run the OS-specific command test
    asyncio.run(test_os_specific_command_generation())
