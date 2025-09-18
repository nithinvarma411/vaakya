"""
Modular Cross-Platform Agent

Uses modular operations system with OS detection and plugin architecture:
1. App Operations - Cross-platform app launching with fuzzy search
2. File Operations - File/folder management
3. Web Operations - Web search without browser

All operations are modular and platform-aware.
"""

import os
import platform
import logging
from typing import List, Dict, Any

# Set tokenizer parallelism to avoid warnings
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

import kani
from kani import ai_function, ChatMessage
from kani.engines.llamacpp import LlamaCppEngine
from kani.model_specific import prompt_pipeline_for_hf_model
from .model_utils import ModelDownloader
from .qwen_parser import QwenToolCallParser
from .operations import AppOperations, FileOperations, WebOperations

# Import transcription service
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from src.app.services.transcription_service import TranscriptionService

log = logging.getLogger(__name__)

class WorkingAgent(kani.Kani):
    """
    Modular Cross-Platform Agent with platform-aware operations:
    - App Operations (fuzzy search app launching)
    - File Operations (file/folder management)  
    - Web Operations (DuckDuckGo search)
    """
    
    def __init__(self, model_name: str = "qwen2.5-1.5b-instruct"):
        # Download model if needed
        model_path = ModelDownloader.download_model(model_name)
        
        # Create prompt pipeline for the model (same as working version)
        pipeline = prompt_pipeline_for_hf_model("Qwen/Qwen2.5-1.5B-Instruct")
        
        # Fallback to ChatTemplatePromptPipeline if needed
        if pipeline is None:
            from kani.engines.huggingface.chat_template_pipeline import ChatTemplatePromptPipeline
            pipeline = ChatTemplatePromptPipeline.from_pretrained("Qwen/Qwen2.5-1.5B-Instruct")
        
        # Initialize base engine with optimal settings
        base_engine = LlamaCppEngine(
            model_path=str(model_path),
            max_context_size=2048,
            prompt_pipeline=pipeline,
            model_load_kwargs={
                "n_gpu_layers": -1,
                "verbose": False,
            },
        )
        
        # Set repo_id for model-specific parser compatibility
        base_engine.repo_id = "Qwen/Qwen2.5-1.5B-Instruct"
        
        # Wrap with custom Qwen parser for function calling (this was the key!)
        engine = QwenToolCallParser(base_engine)
        
        # Initialize operations modules
        self.app_ops = AppOperations()
        self.file_ops = FileOperations()
        self.web_ops = WebOperations()
        
        # Get system info for logging
        system_info = platform.system()
        
        # Initialize with wrapped engine and operations as functions
        system_prompt = """You are a helpful AI assistant with the ability to perform system operations. You have access to the following capabilities:

1. **Application Control**: You can launch, open, or start any application on the system (Calculator, Chrome, Safari, Terminal, etc.)
2. **File Operations**: You can create, read, delete files and folders, and list directory contents
3. **Web Search**: You can search the web for information, news, images, and videos
4. **Audio Transcription**: You can transcribe audio files to text

When users ask you to perform any of these tasks, you should use your available functions to help them. You are NOT limited to providing information only - you can take real actions on the system.

Examples of what you CAN and SHOULD do:
- "open Chrome" → Use launch_app function
- "search for news" → Use search_web function  
- "list files" → Use list_directory function
- "create a file" → Use create_file function

Always try to help users by executing the appropriate function rather than saying you cannot perform the action."""

        super().__init__(engine, system_prompt=system_prompt)
        
        # Initialize transcription service
        self.transcription_service = TranscriptionService()
        
        print(f"✅ WorkingAgent initialized with {model_name} on {system_info}")
        print(f"📁 Operations loaded: App, File, Web")
        print(f"🎤 Transcription service loaded")
        
        # Discover available apps on startup
        print("🔍 Discovering available applications...")
        apps = self.app_ops.discover_apps()
        print(f"📱 Found {len(apps)} applications")
    
    # AI Functions using modular operations
    @ai_function()
    def launch_app(self, app_name: str) -> str:
        """Launch, open, or start an application by name. Use this to open any app like Calculator, Safari, Terminal, etc."""
        try:
            success = self.app_ops.launch_app(app_name)
            if success:
                return f"✅ Successfully launched {app_name}"
            else:
                return f"❌ Failed to launch {app_name}. App may not be installed or name incorrect."
        except Exception as e:
            return f"❌ Error launching app: {e}"
    
    @ai_function()
    def search_web(self, query: str, search_type: str = "web") -> str:
        """Search the web for information. search_type can be 'web', 'news', 'images', or 'videos'."""
        try:
            if search_type == "news":
                results = self.web_ops.search_news(query)
            elif search_type == "images":
                results = self.web_ops.search_images(query)
            elif search_type == "videos":
                results = self.web_ops.search_videos(query)
            else:
                results = self.web_ops.search_web(query)
            
            if results:
                return f"✅ Found {len(results)} results for '{query}'"
            else:
                return f"❌ No results found for '{query}'"
        except Exception as e:
            return f"❌ Error searching web: {e}"
    
    @ai_function()
    def create_file(self, file_path: str, content: str = "") -> str:
        """Create a new file with optional content."""
        try:
            success = self.file_ops.create_file(file_path, content)
            if success:
                return f"✅ Created file: {file_path}"
            else:
                return f"❌ Failed to create file: {file_path}"
        except Exception as e:
            return f"❌ Error creating file: {e}"
    
    @ai_function()
    def create_folder(self, folder_path: str) -> str:
        """Create a new folder."""
        try:
            success = self.file_ops.create_folder(folder_path)
            if success:
                return f"✅ Created folder: {folder_path}"
            else:
                return f"❌ Failed to create folder: {folder_path}"
        except Exception as e:
            return f"❌ Error creating folder: {e}"
    
    @ai_function()
    def delete_file(self, file_path: str) -> str:
        """Delete a file."""
        try:
            success = self.file_ops.delete_file(file_path)
            if success:
                return f"✅ Deleted file: {file_path}"
            else:
                return f"❌ Failed to delete file: {file_path}"
        except Exception as e:
            return f"❌ Error deleting file: {e}"
    
    @ai_function()
    def delete_folder(self, folder_path: str) -> str:
        """Delete a folder and its contents."""
        try:
            success = self.file_ops.delete_folder(folder_path)
            if success:
                return f"✅ Deleted folder: {folder_path}"
            else:
                return f"❌ Failed to delete folder: {folder_path}"
        except Exception as e:
            return f"❌ Error deleting folder: {e}"
    
    @ai_function()
    def list_directory(self, directory_path: str) -> str:
        """List contents of a directory."""
        try:
            contents = self.file_ops.list_directory(directory_path)
            if contents is not None:
                return f"✅ Listed directory: {directory_path}"
            else:
                return f"❌ Failed to list directory: {directory_path}"
        except Exception as e:
            return f"❌ Error listing directory: {e}"
    
    @ai_function()
    def read_file(self, file_path: str) -> str:
        """Read content from a file."""
        try:
            content = self.file_ops.read_file(file_path)
            if content is not None:
                return f"✅ Read file: {file_path}\n\nContent:\n{content}"
            else:
                return f"❌ Failed to read file: {file_path}"
        except Exception as e:
            return f"❌ Error reading file: {e}"
    
    @ai_function()
    def write_file(self, file_path: str, content: str, append: bool = False) -> str:
        """Write content to a file."""
        try:
            success = self.file_ops.write_file(file_path, content, append)
            action = "Appended to" if append else "Wrote to"
            if success:
                return f"✅ {action} file: {file_path}"
            else:
                return f"❌ Failed to write to file: {file_path}"
        except Exception as e:
            return f"❌ Error writing file: {e}"
    
    @ai_function()
    def copy_file(self, source: str, destination: str) -> str:
        """Copy a file from source to destination."""
        try:
            success = self.file_ops.copy_file(source, destination)
            if success:
                return f"✅ Copied {source} to {destination}"
            else:
                return f"❌ Failed to copy file"
        except Exception as e:
            return f"❌ Error copying file: {e}"
    
    @ai_function()
    def move_file(self, source: str, destination: str) -> str:
        """Move a file from source to destination."""
        try:
            success = self.file_ops.move_file(source, destination)
            if success:
                return f"✅ Moved {source} to {destination}"
            else:
                return f"❌ Failed to move file"
        except Exception as e:
            return f"❌ Error moving file: {e}"
    
    @ai_function()
    def transcribe_audio(self, audio_file_path: str) -> str:
        """Transcribe an audio file to text. Use this to convert speech in audio files to text."""
        try:
            # Check if file exists
            if not os.path.exists(audio_file_path):
                return f"❌ Audio file not found: {audio_file_path}"
            
            # Transcribe the audio file
            import asyncio
            transcription = asyncio.run(self.transcription_service.transcribe_file(audio_file_path))
            
            if transcription:
                return f"✅ Transcription completed:\n{transcription}"
            else:
                return f"❌ Failed to transcribe audio file: {audio_file_path}"
        except Exception as e:
            return f"❌ Error transcribing audio: {e}"


# Helper functions for creating and testing the agent
async def create_working_agent() -> WorkingAgent:
    """Create a new WorkingAgent instance."""
    return WorkingAgent()

async def test_working_agent():
    """Test the working agent with basic functionality."""
    print("🧪 Testing WorkingAgent...")
    
    # Create agent
    agent = await create_working_agent()
    
    # Test conversation
    test_queries = [
        "search the web for latest AI news",
        "list files in the current directory", 
        "what apps do you have available?"
    ]
    
    for query in test_queries:
        print(f"\n👤 User: {query}")
        # Use the correct kani method for chat
        async for message in agent.full_round(query):
            if message.role == "assistant":
                print(f"🤖 Agent: {message.content}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_working_agent())