"""
Smart Agent with Auto-Download and Plugin-Based Function Calling

This agent uses Qwen2.5-1.5B-Instruct for reliable function calling and automatically
downloads        # Get all available functions from operations modules
        operation_functions = get_all_functions()
        
        # Initialize Kani with engine and dynamic functions
        super().__init__(engine, functions=operation_functions)
        
        # Set system prompt after initialization
        system_prompt = self._create_system_prompt()
        self.chat_history = [ChatMessage.system(system_prompt)]
        
        print(f"✅ SmartAgent initialized with {model_name}")
        print(f"🖥️  Platform: {PlatformUtils.get_system_type()}")
        print(f"📱 Loaded {len(operation_functions)} operations")
        
        # List loaded functions for debugging
        function_names = [f.name for f in operation_functions]
        print(f"🔧 Available functions: {', '.join(function_names)}") present. Features a plugin-based operations system.
"""

import os
import json
import re
import subprocess
import platform
import urllib.request
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import asyncio

# Set tokenizer parallelism to avoid warnings
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

import kani
from kani import ai_function, ChatMessage
from kani.engines.llamacpp import LlamaCppEngine
from kani.model_specific import prompt_pipeline_for_hf_model
from kani.model_specific.base import BaseToolCallParser
from kani.models import ToolCall, FunctionCall
import logging
from .qwen_parser import QwenToolCallParser

log = logging.getLogger(__name__)

import kani
from kani import AIFunction, ai_function, ChatMessage
from kani.engines.llamacpp import LlamaCppEngine
from kani.model_specific import prompt_pipeline_for_hf_model
from .operations import get_all_functions
from .operations.utils import PlatformUtils

class ModelDownloader:
    """Handles automatic model downloading."""
    
    MODEL_INFO = {
        "qwen2.5-1.5b-instruct": {
            "filename": "qwen2.5-1.5b-instruct-q4_k_m.gguf",
            "url": "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf",
            "size_mb": 950
        }
    }
    
    @staticmethod
    def get_models_dir() -> Path:
        """Get the models directory relative to the project root."""
        # Navigate from src/app/agent/ to models/
        current_dir = Path(__file__).parent
        project_root = current_dir.parent.parent.parent
        models_dir = project_root / "models"
        models_dir.mkdir(exist_ok=True)
        return models_dir
    
    @staticmethod
    def download_model(model_name: str) -> Path:
        """Download model if not present and return path."""
        if model_name not in ModelDownloader.MODEL_INFO:
            raise ValueError(f"Unknown model: {model_name}")
        
        model_info = ModelDownloader.MODEL_INFO[model_name]
        models_dir = ModelDownloader.get_models_dir()
        model_path = models_dir / model_info["filename"]
        
        if model_path.exists():
            print(f"✅ Model already exists: {model_path}")
            return model_path
        
        print(f"📥 Downloading {model_name} ({model_info['size_mb']}MB)...")
        print(f"📍 URL: {model_info['url']}")
        print(f"💾 Saving to: {model_path}")
        
        try:
            def progress_hook(block_num, block_size, total_size):
                if total_size > 0:
                    percent = min(100, (block_num * block_size * 100) // total_size)
                    print(f"\r⏳ Download progress: {percent}%", end="", flush=True)
            
            urllib.request.urlretrieve(model_info["url"], model_path, progress_hook)
            print(f"\n✅ Download complete: {model_path}")
            return model_path
            
        except Exception as e:
            print(f"\n❌ Download failed: {e}")
            if model_path.exists():
                model_path.unlink()  # Remove incomplete file
            raise

class SmartAgent(kani.Kani):
    """
    Smart Agent with reliable function calling using Qwen2.5-1.5B-Instruct.
    
    Features:
    - Auto-downloads model if not present
    - Plugin-based operations system
    - Dynamic function registration
    - Reliable JSON parsing
    - Clean function calling interface
    """
    
    def __init__(self, model_name: str = "qwen2.5-1.5b-instruct"):
        # Download model if needed
        model_path = ModelDownloader.download_model(model_name)
        
        # Create prompt pipeline for the model
        pipeline = prompt_pipeline_for_hf_model("Qwen/Qwen2.5-1.5B-Instruct")
        
        # Extract model name from filename for better Kani compatibility
        model_filename = model_path.name
        if "qwen" in model_filename.lower():
            # Use the Qwen model repo ID for proper function calling support
            derived_repo_id = "Qwen/Qwen2.5-1.5B-Instruct"
        else:
            derived_repo_id = "microsoft/DialoGPT-medium"  # fallback
        
        # Ensure we have a pipeline
        if pipeline is None:
            from kani.engines.huggingface.chat_template_pipeline import ChatTemplatePromptPipeline
            # Create a basic pipeline - Kani will use the model's built-in chat template
            pipeline = ChatTemplatePromptPipeline.from_pretrained("Qwen/Qwen2.5-1.5B-Instruct")
        
        # Initialize engine with optimal settings for function calling
        base_engine = LlamaCppEngine(
            model_path=str(model_path),
            max_context_size=2048,
            prompt_pipeline=pipeline,
            model_load_kwargs={
                "n_gpu_layers": -1,  # Use GPU if available - this is a model loading param
                "verbose": False,    # Reduce verbosity
            },
        )
        
        # Set repo_id on base engine for model-specific parser compatibility
        base_engine.repo_id = derived_repo_id
        
        # Wrap with custom Qwen parser for function calling
        engine = QwenToolCallParser(base_engine)
        
        # Get all available functions from operations modules
        operation_functions = get_all_functions()
        
        # Initialize Kani with engine and dynamic functions
        super().__init__(engine, functions=operation_functions)
        
        # Set system prompt after initialization
        system_prompt = self._create_system_prompt()
        self.chat_history = [ChatMessage.system(system_prompt)]
        
        print(f"✅ SmartAgent initialized with {model_name}")
        print(f"🖥️  Platform: {platform.system().lower()}")
        print(f"📱 Loaded {len(operation_functions)} operations")
        
        # List loaded functions for debugging
        function_names = [f.name for f in operation_functions]
        print(f"� Available functions: {', '.join(function_names)}")
    
    def _create_system_prompt(self) -> str:
        """Create a completely generic system prompt for function calling."""
        return """You are a helpful AI assistant with access to various functions that can help users accomplish their tasks.

When users make requests, analyze their intent and use the most appropriate available function to help them. Always be helpful, clear, and try your best to accomplish what the user is asking for.

Use your judgment to interpret natural language requests and map them to the right function calls with appropriate parameters."""
    async def chat_with_user(self, message: str) -> str:
        """Chat with the user and handle function calling automatically."""
        try:
            # Use full_round for complete conversation turn with function calling
            final_response = None
            async for msg in self.full_round(message):
                # Always update final_response with the latest assistant message that has content
                if str(msg.role).endswith('ASSISTANT'):  # Handle both ChatRole.ASSISTANT and 'assistant'
                    content = msg.content
                    if isinstance(content, str) and content.strip():
                        final_response = content
                    elif isinstance(content, list):
                        result = " ".join(str(part) for part in content)
                        if result.strip():
                            final_response = result
            
            # Return the final response or a default message
            return final_response or "No response generated"
        except Exception as e:
            return f"❌ Error in chat: {str(e)}"

# Convenience function for easy usage
async def create_smart_agent() -> SmartAgent:
    """Create a SmartAgent with default settings."""
    return SmartAgent()

async def test_smart_agent():
    """Test the SmartAgent functionality."""
    print("🧪 Testing SmartAgent...")
    
    agent = await create_smart_agent()
    
    test_messages = [
        "what time is it?",
        "open Chrome",
        "launch Spotify", 
        "play some music",
        "search for funny cats",
        "open Google",
        "what's my memory usage?",
        "launch Calculator",
        "open VS Code"
    ]
    
    for message in test_messages:
        print(f"\n👤 User: {message}")
        response = await agent.chat_with_user(message)
        print(f"🤖 Agent: {response}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_smart_agent())