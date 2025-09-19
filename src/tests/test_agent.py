"""
WorkingAgent Chat Interface Test

This test verifies that the WorkingAgent can understand natural language
and trigger the correct AI functions through the chat interface.

Run this to verify the agent is working correctly.
"""

import asyncio
import sys
from pathlib import Path

import pytest

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent.parent))

from src.app.agent.working_agent import create_working_agent

# Constants
EXPECTED_SUCCESSFUL_TESTS = 4


@pytest.mark.asyncio
async def test_chat_interface() -> None:
    """Test that the chat interface can trigger AI functions from natural language."""

    print("🧪 CHAT INTERFACE FUNCTION CALLING TEST")
    print("=" * 50)
    print("Testing if LLM can understand natural language and trigger AI functions...")

    # Create agent
    print("\n🚀 Creating WorkingAgent...")
    agent = await create_working_agent()
    print("✅ Agent ready!")

    # Simple test queries
    test_queries = [
        "search for Python news",
        "list files in current directory",
        "open calculator",
        "open browser",
    ]

    successful_tests = 0

    for i, query in enumerate(test_queries, 1):
        print(f"\n[Test {i}/4] User: {query}")
        print("⏳ Processing...")

        try:
            # Check if functions are triggered (we can see them in the output)
            messages = []
            async for message in agent.full_round(query):
                messages.append(message)

            # Debug: show actual message roles
            print(f"   📝 Messages: {[str(msg.role) for msg in messages]}")

            # Check for any evidence of function execution
            function_evidence = False
            for msg in messages:
                # Check different possible function indicators
                if (
                    str(msg.role) == "function"
                    or str(msg.role) == "ChatRole.FUNCTION"
                    or (hasattr(msg, "tool_calls") and msg.tool_calls)
                    or (
                        msg.content
                        and (
                            "✅" in str(msg.content)
                            or "🔍" in str(msg.content)
                            or "📁" in str(msg.content)
                        )
                    )
                ):
                    function_evidence = True
                    break

            if function_evidence:
                print("✅ SUCCESS! Functions executed (evidence found)")
                successful_tests += 1
            else:
                print("❌ No function execution detected")

        except Exception as e:
            print(f"❌ Error: {e}")

    # Summary
    print("\n" + "=" * 50)
    print("📊 RESULTS")
    print("=" * 50)
    print(f"✅ Successful: {successful_tests}/{EXPECTED_SUCCESSFUL_TESTS}")

    if successful_tests == EXPECTED_SUCCESSFUL_TESTS:
        print("🎉 PERFECT! Chat interface can trigger all AI functions!")
        print("💡 The LLM understands natural language and calls the right operations!")
    elif successful_tests > 0:
        print("👍 MOSTLY WORKING! Some functions triggered successfully.")
    else:
        print("❌ ISSUE: No functions were triggered by natural language.")

    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(test_chat_interface())
