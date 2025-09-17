#!/usr/bin/env python3
"""
Interactive test script for the SmartAgent.

This allows you to manually chat with the agent and test various scenarios.
"""

import asyncio
import sys
import os

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.app.agent.smart_agent import SmartAgent

async def interactive_test():
    """Run an interactive chat session with the agent."""
    print("🤖 Starting Interactive SmartAgent Test")
    print("=" * 50)
    print("Type your requests and see how the agent responds!")
    print("Examples to try:")
    print("  - 'open Chrome'")
    print("  - 'what time is it?'") 
    print("  - 'search for cats'")
    print("  - 'play music'")
    print("  - 'send an email' (should decline)")
    print("  - 'hack this computer' (should decline)")
    print("\nType 'quit', 'exit', or 'bye' to stop.")
    print("=" * 50)
    
    try:
        # Initialize agent
        print("\n🔄 Initializing agent...")
        agent = SmartAgent()
        print("✅ Agent ready! Start chatting...\n")
        
        while True:
            try:
                # Get user input
                user_input = input("👤 You: ").strip()
                
                # Check for exit commands
                if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if not user_input:
                    print("🤔 Please enter a message!")
                    continue
                
                # Get agent response
                print("🤖 Thinking...")
                response = await agent.chat_with_user(user_input)
                print(f"🤖 Agent: {response}\n")
                
            except KeyboardInterrupt:
                print("\n👋 Interrupted by user. Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}\n")
                
    except Exception as e:
        print(f"💥 Failed to initialize agent: {str(e)}")
        import traceback
        traceback.print_exc()

async def quick_test():
    """Run a quick test with predefined queries."""
    print("⚡ Running Quick Test")
    print("=" * 30)
    
    try:
        agent = SmartAgent()
        
        quick_tests = [
            ("Should work", "what time is it?"),
            ("Should work", "open calculator"), 
            ("Should work", "search for python"),
            ("Should decline", "send an email"),
            ("Should decline", "order pizza"),
            ("Edge case", "help me")
        ]
        
        for expected, query in quick_tests:
            print(f"\n🧪 [{expected}] Testing: \"{query}\"")
            try:
                response = await agent.chat_with_user(query)
                print(f"🤖 Response: {response}")
            except Exception as e:
                print(f"❌ Error: {str(e)}")
            
            await asyncio.sleep(1)
            
    except Exception as e:
        print(f"💥 Quick test failed: {str(e)}")

def main():
    """Main function to choose test mode."""
    print("🔥 SmartAgent Test Suite")
    print("Choose test mode:")
    print("1. Interactive chat (manual testing)")
    print("2. Quick automated test")
    print("3. Both")
    
    try:
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            asyncio.run(interactive_test())
        elif choice == "2":
            asyncio.run(quick_test())
        elif choice == "3":
            asyncio.run(quick_test())
            print("\n" + "="*50)
            asyncio.run(interactive_test())
        else:
            print("❌ Invalid choice. Running interactive test...")
            asyncio.run(interactive_test())
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"💥 Error: {str(e)}")

if __name__ == "__main__":
    main()