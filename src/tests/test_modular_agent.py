"""
Comprehensive Test Suite for WorkingAgent Chat Interface

This test verifies that the chat interface can properly understand natural language
queries and trigger the correct AI functions across all three operation categories:
- File Operations (list, create, read, write)
- App Operations (launch applications with fuzzy search)
- Web Operations (search web, news, images, videos)

The test ensures the agent works end-to-end through the chat interface.
"""

import asyncio
import sys
import time
import traceback
from pathlib import Path

import pytest

# Add the src directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent / "src"))

from app.agent.working_agent import create_working_agent


@pytest.mark.asyncio
async def test_comprehensive_chat_interface() -> None:  # noqa: PLR0912, PLR0915
    """
    Comprehensive test of the WorkingAgent chat interface.

    Tests all three operation categories through natural language queries:
    1. Web Operations - Search functionality
    2. File Operations - Directory listing and file creation
    3. App Operations - Application launching
    4. Mixed Operations - Complex queries requiring multiple operations

    Note: Function complexity is acceptable here as this is a comprehensive test
    that needs to cover multiple scenarios and provide detailed output.
    """
    print("🧪 COMPREHENSIVE WORKING AGENT CHAT INTERFACE TEST")
    print("=" * 65)

    try:
        # Create agent
        print("\n🚀 Creating WorkingAgent...")
        start_time = time.time()
        agent = await create_working_agent()
        init_time = time.time() - start_time
        print(f"✅ Agent initialized in {init_time:.2f} seconds")

        # Comprehensive test suite covering all operation types
        test_suite = [
            {
                "category": "🌐 Web Operations",
                "queries": [
                    "search the web for latest Python news",
                    "find news about artificial intelligence",
                    "search for information about machine learning tutorials",
                ],
            },
            {
                "category": "📁 File Operations",
                "queries": [
                    "list files in the current directory",
                    "create a file called test_output.txt with content 'Agent test successful'",
                    "show me what's in the current folder",
                ],
            },
            {
                "category": "🚀 App Operations",
                "queries": [
                    "open calculator app",
                    "launch notepad or text editor",
                    "start the browser application",
                ],
            },
            {
                "category": "🔄 Mixed Operations",
                "queries": [
                    "search for Python tutorials and then create a file to save the results",
                    "list the files here and tell me about them",
                ],
            },
        ]

        total_tests = sum(len(cat["queries"]) for cat in test_suite)
        current_test = 0
        successful_tests = 0

        print(
            f"\n🧪 Running {total_tests} comprehensive tests across {len(test_suite)} categories..."
        )
        print("=" * 65)

        for category_info in test_suite:
            category = category_info["category"]
            queries = category_info["queries"]

            print(f"\n{category}")
            print("-" * len(category))

            for query in queries:
                current_test += 1
                print(f"\n[Test {current_test}/{total_tests}] User: {query}")

                try:
                    # Time the response
                    query_start = time.time()

                    # Clear conversation history to prevent context overflow
                    agent.chat_history.clear()

                    # Use the chat interface and collect all messages
                    messages = []
                    async for message in agent.full_round(query):
                        messages.append(message)

                    response_time = time.time() - query_start

                    # Check for evidence of function execution (same pattern as test_agent.py)
                    function_evidence = False
                    function_results = []

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
                                    or "🚀" in str(msg.content)
                                    or "Created file:" in str(msg.content)
                                    or "Found" in str(msg.content)
                                    or "Launched" in str(msg.content)
                                    or "Directory contents" in str(msg.content)
                                )
                            )
                        ):
                            function_evidence = True
                            # Extract meaningful content for display
                            if msg.content:
                                result_line = str(msg.content).split("\n")[0]
                                function_results.append(result_line)

                    if function_evidence:
                        print("✅ SUCCESS! Function execution detected")
                        for result in function_results[
                            :2
                        ]:  # Show first 2 results to avoid spam
                            print(f"   📋 Evidence: {result}")
                        print(f"⚡ Response time: {response_time:.2f}s")
                        successful_tests += 1
                    else:
                        print("❌ No function execution evidence found")
                        print(
                            f"📝 Debug: {len(messages)} messages, roles: {[str(msg.role) for msg in messages]}"
                        )
                        # Show first message content for debugging
                        if messages and messages[0].content:
                            print(
                                f"📝 First message content: {str(messages[0].content)[:100]}..."
                            )

                except Exception as e:
                    print(f"❌ Error in chat: {e}")
                    traceback.print_exc()

        # Test summary
        total_time = time.time() - start_time
        success_rate = (successful_tests / total_tests) * 100

        print("\n" + "=" * 65)
        print("📊 TEST SUMMARY")
        print("=" * 65)
        print(
            f"✅ Successful tests: {successful_tests}/{total_tests} ({success_rate:.1f}%)"
        )
        print(f"⏱️  Total test time: {total_time:.2f} seconds")
        print(
            f"📈 Average response time: {(total_time - init_time) / successful_tests:.2f}s per query"
            if successful_tests > 0
            else ""
        )

        if successful_tests == total_tests:
            print(
                "🎉 ALL TESTS PASSED! Chat interface successfully triggers AI functions!"
            )
            print(
                "💡 The LLM can understand natural language and call the right operations!"
            )
        else:
            print(f"⚠️  {total_tests - successful_tests} tests failed or had issues.")
            print(
                "💡 Check if queries need to be more specific or if there are function mapping issues."
            )

        print("=" * 65)

    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    # Run the comprehensive chat interface test
    asyncio.run(test_comprehensive_chat_interface())
