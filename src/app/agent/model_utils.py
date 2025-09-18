"""
Model utilities for downloading and managing LLM models.
"""

import urllib.request
from pathlib import Path
from typing import Dict


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