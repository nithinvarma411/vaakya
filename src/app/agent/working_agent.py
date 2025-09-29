"""
Modular Cross-Platform Agent

Uses modular operations system with OS detection and plugin architecture:
1. App Operations - Cross-platform app launching with fuzzy search
2. Web Operations - Web search without browser

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
from .operations import AppOperations, WebOperations
from .operations.utilities import UtilityFunctions
from .qwen_parser import QwenToolCallParser

sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from src.app.services.transcription_service import TranscriptionService

log = logging.getLogger(__name__)


class WorkingAgent(kani.Kani):  # type: ignore[misc]
    """
    Modular Cross-Platform Agent with platform-aware operations:
    - App Operations (fuzzy search app launching)
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
        self.web_ops = WebOperations()
        self.utils = UtilityFunctions()

        # Get system info for logging
        system_info = platform.system()

                # Initialize with wrapped engine and operations as functions
        system_prompt = f"""You COMPLETE TASKS by calling functions until DONE!

- search_web(query, search_type): Search for information  
- execute_shell_command(command): Execute shell commands - USE FOR: ls, pwd, mkdir, ps, etc.
- locate_file_or_folder(name): SMART search for files/folders (searches project locations, finds Git repos)
- locate_application(app_name): Find where an app is installed
- transcribe_audio(audio_file_path): Convert audio to text

SHELL COMMAND TRIGGERS - USE execute_shell_command() for:
- "list files" → execute_shell_command("ls -la")
- "current directory" → execute_shell_command("pwd") 
- "create directory" → execute_shell_command("mkdir dirname")
- "running processes" → execute_shell_command("ps aux")
- "show files" → execute_shell_command("ls")
- Any command-like request → USE SHELL COMMANDS!

For "open X in Y" requests:
1. locate_file_or_folder("X") → get path
2. locate_application("Y") → get app
3. execute_shell_command('open -a Y "/exact/path"')

Always use EXACT path from locate_file_or_folder result!
Put paths with spaces in single quotes in the command!

OS: {platform.system()} ({platform.machine()})"""

        super().__init__(engine, system_prompt=system_prompt)

        # Initialize transcription service
        self.transcription_service = TranscriptionService()

        print(f"✅ WorkingAgent initialized with {model_name} on {system_info}")
        print("📁 Operations loaded: App, Web, Utilities")
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
            if hasattr(self, "web_ops"):
                # WebOperations cleanup if needed
                pass
            if hasattr(self, "utils"):
                # Utility functions cleanup if needed
                pass

            print("WorkingAgent cleanup completed")
        except Exception as e:
            print(f"Error during WorkingAgent cleanup: {e}")

    # AI Functions using modular operations
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
    def execute_shell_command(self, command: str) -> str:
        """Execute a shell command safely."""
        try:
            result = self.utils.execute_shell_command(command)
            if "error" in result:
                return f"❌ Error executing command: {result['error']}"
            else:
                return f"✅ Command executed:\n{result['stdout']}\nStderr: {result['stderr']}"
        except Exception as e:
            return f"❌ Error executing shell command: {e}"

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

    @ai_function()  # type: ignore[misc]
    def locate_application(self, app_name: str) -> str:
        """Locate the path of an application by name using fuzzy search."""
        try:
            app_path = self.utils.locate_app_path(app_name)
            if app_path:
                return f"✅ Found {app_name}: {app_path}"
            else:
                return f"❌ Could not find application: {app_name}"
        except Exception as e:
            return f"❌ Error locating application: {e}"

    @ai_function()  # type: ignore[misc]
    def locate_file_or_folder(self, name: str) -> str:
        """Locate a file or folder by name in common system locations."""
        try:
            path = self.utils.locate_file_or_folder(name)
            if path:
                return f"✅ Found {name}: {path}"
            else:
                return f"❌ Could not find file or folder: {name}"
        except Exception as e:
            return f"❌ Error locating file or folder: {e}"


# Helper functions for creating the agent
async def create_working_agent() -> WorkingAgent:
    """Create a new WorkingAgent instance."""
    return WorkingAgent()
