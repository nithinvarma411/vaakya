#!/usr/bin/env python3
"""
Test edge cases and error handling for the SmartAgent
"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from app.agent.smart_agent import SmartAgent

async def test_edge_cases():
    print("🧪 Testing Edge Cases and Error Handling")
    print("=" * 50)
    
    # Initialize agent
    try:
        agent = SmartAgent()
        print("✅ Agent initialized successfully")
        print()
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        return
    
    # Test cases that should fail gracefully
    test_cases = [
        "Launch nonexistentapp123",  # Non-existent app
        "Open some_fake_application",  # Another non-existent app  
        "Start XYZ editor",  # Vague non-existent app
        "Launch photoshop",  # App that might not be installed
        "Open microsoft word",  # App that might not be installed
    ]
    
    for i, request in enumerate(test_cases, 1):
        print(f"🔍 Test {i}: \"{request}\"")
        print("-" * 40)
        try:
            response = await agent.chat_with_user(request)
            print(f"🤖 Response: {response}")
        except Exception as e:
            print(f"❌ Error: {e}")
        print()
    
    print("=" * 50)
    print("✅ Edge case testing completed!")

if __name__ == "__main__":
    asyncio.run(test_edge_cases())