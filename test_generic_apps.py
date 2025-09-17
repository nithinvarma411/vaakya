#!/usr/bin/env python3
"""
Test generic app requests like 'browser', 'code editor', etc.
"""

import asyncio
import sys
import os

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.app.agent.smart_agent import SmartAgent

async def test_generic_requests():
    """Test how the agent handles generic app requests."""
    print("🧪 Testing Generic App Requests")
    print("=" * 50)
    
    try:
        agent = SmartAgent()
        print("\n✅ Agent initialized successfully")
        
        test_cases = [
            "Open a browser",
            "Launch my code editor", 
            "Start a music player",
            "Open text editor",
            "Launch terminal",
            "Open calculator",
            "Start video player"
        ]
        
        for i, test in enumerate(test_cases, 1):
            print(f"\n🔍 Test {i}: \"{test}\"")
            print("-" * 40)
            
            try:
                response = await agent.chat_with_user(test)
                print(f"🤖 Response: {response}")
            except Exception as e:
                print(f"❌ Error: {str(e)}")
            
            await asyncio.sleep(1)
        
        print("\n" + "=" * 50)
        print("✅ Generic request test completed!")
        
    except Exception as e:
        print(f"💥 Failed to initialize agent: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_generic_requests())