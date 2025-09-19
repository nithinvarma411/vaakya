"""
Model utilities for downloading and managing LLM models.
"""

import socket
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, ClassVar, Dict, Optional

from src.app.config.settings import settings


class ModelDownloader:
    """Handles automatic model downloading."""

    MODEL_INFO: ClassVar[Dict[str, Dict[str, Any]]] = settings.model.MODEL_INFO

    @staticmethod
    def get_models_dir() -> Path:
        """Get the models directory from settings."""
        models_dir = settings.models_dir
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
            return model_path  # type: ignore[no-any-return]

        print(f"📥 Downloading {model_name} ({model_info['size_mb']}MB)...")
        print(f"📍 URL: {model_info['url']}")
        print(f"💾 Saving to: {model_path}")

        # Set socket timeout to prevent hanging on Windows
        original_timeout: Optional[float] = socket.getdefaulttimeout()

        try:
            socket.setdefaulttimeout(30)  # 30 seconds timeout

            def progress_hook(block_num: int, block_size: int, total_size: int) -> None:
                if total_size > 0:
                    percent = min(100, (block_num * block_size * 100) // total_size)
                    print(f"\r⏳ Download progress: {percent}%", end="", flush=True)
                else:
                    # Show downloaded bytes when total size is unknown
                    downloaded = block_num * block_size
                    print(
                        f"\r⏳ Downloaded: {downloaded // (1024 * 1024)}MB",
                        end="",
                        flush=True,
                    )

            print("🔗 Starting download...")
            urllib.request.urlretrieve(model_info["url"], model_path, progress_hook)
            print(f"\n✅ Download complete: {model_path}")

            return model_path  # type: ignore[no-any-return]

        except socket.timeout as e:
            print("\n❌ Download timed out after 30 seconds")
            if model_path.exists():
                model_path.unlink()  # Remove incomplete file
            raise Exception(
                "Download timed out - please check your internet connection"
            ) from e
        except urllib.error.URLError as e:
            print(f"\n❌ Network error: {e}")
            if model_path.exists():
                model_path.unlink()  # Remove incomplete file
            raise Exception(f"Network error during download: {e}") from e
        except Exception as e:
            print(f"\n❌ Download failed: {e}")
            if model_path.exists():
                model_path.unlink()  # Remove incomplete file
            raise
        finally:
            # Always restore original timeout
            socket.setdefaulttimeout(original_timeout)
