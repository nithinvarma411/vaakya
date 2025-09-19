"""
Modular Cross-Platform Agent

Uses modular operations system with OS detection and plugin architecture:
1. App Operations - Cross-platform app launching with fuzzy search
2. File Operations - File/folder management
3. Web Operations - Web search without browser

All operations are modular and platform-aware.
"""

import asyncio
import logging
import os
import platform
import sys
from pathlib import Path
from typing import Optional

# Set tokenizer parallelism to avoid warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import kani
from kani import ai_function
from kani.engines.llamacpp import LlamaCppEngine
from kani.model_specific import prompt_pipeline_for_hf_model

try:
    from kani.engines.huggingface.chat_template_pipeline import (
        ChatTemplatePromptPipeline,
    )
except ImportError:
    ChatTemplatePromptPipeline = None

from src.app.config.settings import settings

from .model_utils import ModelDownloader
from .operations import AppOperations, FileOperations, WebOperations
from .qwen_parser import QwenToolCallParser

sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from src.app.services.transcription_service import TranscriptionService

log = logging.getLogger(__name__)


class WorkingAgent(kani.Kani):  # type: ignore[misc]
    """
    Modular Cross-Platform Agent with platform-aware operations:
    - App Operations (fuzzy search app launching)
    - File Operations (file/folder management)
    - Web Operations (DuckDuckGo search)
    """

    def __init__(self, model_name: Optional[str] = None) -> None:
        # Use default model from settings if none provided
        if model_name is None:
            model_name = settings.model.DEFAULT_MODEL_NAME

        # Download model if needed
        model_path = ModelDownloader.download_model(model_name)

        # Create prompt pipeline for the model (same as working version)
        pipeline = prompt_pipeline_for_hf_model("Qwen/Qwen2.5-1.5B-Instruct")

        # Fallback to ChatTemplatePromptPipeline if needed
        if pipeline is None and ChatTemplatePromptPipeline is not None:
            pipeline = ChatTemplatePromptPipeline.from_pretrained(
                "Qwen/Qwen2.5-1.5B-Instruct"
            )

        # Ensure we have a valid pipeline before initializing engine
        if pipeline is None:
            raise RuntimeError("Could not create a valid prompt pipeline for the model")

        # Initialize base engine with optimal settings
        base_engine = LlamaCppEngine(
            model_path=str(model_path),
            max_context_size=settings.model.MAX_CONTEXT_SIZE,
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
        system_prompt = """You are a helpful AI assistant with system operation capabilities. You MUST use your available functions when users request actions.

**YOUR FUNCTIONS:**
- launch_app(app_name) - Launch applications
- search_web(query, search_type) - Search web/news/images/videos
- create_file(file_path, content) - Create files
- create_folder(folder_path) - Create folders
- delete_file(file_path) - Delete files
- delete_folder(folder_path) - Delete folders
- list_directory(directory_path) - List directory contents
- read_file(file_path) - Read file contents
- write_file(file_path, content, append) - Write to files
- copy_file(source, destination) - Copy files
- move_file(source, destination) - Move files
- transcribe_audio(audio_file_path) - Transcribe audio

**IMPORTANT: Always use functions when users request actions that match these capabilities:**
- For web searches: "search for X", "find information about Y", "look up Z"
- For file operations: "list files", "create a file", "show me files", "what's in this folder"
- For app launching: "open calculator", "launch notepad", "start browser"

**Examples:**
- User: "list the files here" → Use list_directory function
- User: "search for Python news" → Use search_web function
- User: "open calculator" → Use launch_app function

Be helpful and use the appropriate function for each request."""

        super().__init__(engine, system_prompt=system_prompt)

        # Initialize transcription service
        self.transcription_service = TranscriptionService()

        print(f"✅ WorkingAgent initialized with {model_name} on {system_info}")
        print("📁 Operations loaded: App, File, Web")
        print("🎤 Transcription service loaded")

        # Discover available apps on startup
        print("🔍 Discovering available applications...")
        apps = self.app_ops.discover_apps()
        print(f"📱 Found {len(apps)} applications")

    def cleanup(self) -> None:
        """Clean up resources used by the working agent."""
        try:
            print("Cleaning up WorkingAgent resources...")

            # Clean up transcription service
            if hasattr(self, "transcription_service"):
                self.transcription_service.cleanup()

            # Clean up operations modules
            if hasattr(self, "app_ops"):
                # AppOperations cleanup if needed
                pass
            if hasattr(self, "file_ops"):
                # FileOperations cleanup if needed
                pass
            if hasattr(self, "web_ops"):
                # WebOperations cleanup if needed
                pass

            print("WorkingAgent cleanup completed")
        except Exception as e:
            print(f"Error during WorkingAgent cleanup: {e}")

    # AI Functions using modular operations
    @ai_function()  # type: ignore[misc]
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

    @ai_function()  # type: ignore[misc]
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

    @ai_function()  # type: ignore[misc]
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

    @ai_function()  # type: ignore[misc]
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

    @ai_function()  # type: ignore[misc]
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

    @ai_function()  # type: ignore[misc]
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

    @ai_function()  # type: ignore[misc]
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

    @ai_function()  # type: ignore[misc]
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

    @ai_function()  # type: ignore[misc]
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

    @ai_function()  # type: ignore[misc]
    def copy_file(self, source: str, destination: str) -> str:
        """Copy a file from source to destination."""
        try:
            success = self.file_ops.copy_file(source, destination)
            if success:
                return f"✅ Copied {source} to {destination}"
            else:
                return "❌ Failed to copy file"
        except Exception as e:
            return f"❌ Error copying file: {e}"

    @ai_function()  # type: ignore[misc]
    def move_file(self, source: str, destination: str) -> str:
        """Move a file from source to destination."""
        try:
            success = self.file_ops.move_file(source, destination)
            if success:
                return f"✅ Moved {source} to {destination}"
            else:
                return "❌ Failed to move file"
        except Exception as e:
            return f"❌ Error moving file: {e}"

    @ai_function()  # type: ignore[misc]
    def transcribe_audio(self, audio_file_path: str) -> str:
        """Transcribe an audio file to text. Use this to convert speech in audio files to text."""
        try:
            # Check if file exists
            if not os.path.exists(audio_file_path):
                return f"❌ Audio file not found: {audio_file_path}"

            # Transcribe the audio file
            transcription = asyncio.run(
                self.transcription_service.transcribe_file(audio_file_path)
            )

            if transcription:
                return f"✅ Transcription completed:\n{transcription}"
            else:
                return f"❌ Failed to transcribe audio file: {audio_file_path}"
        except Exception as e:
            return f"❌ Error transcribing audio: {e}"


# Helper functions for creating the agent
async def create_working_agent() -> WorkingAgent:
    """Create a new WorkingAgent instance."""
    return WorkingAgent()
