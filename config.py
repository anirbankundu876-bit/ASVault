"""
App settings, model config, API key loading
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class Config:
    """Configuration manager for ASVault"""

    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)

        self.settings_file = self.config_dir / "settings.json"
        self.keys_file = Path("keys.json")  # gitignored

        self.settings = {}
        self.api_keys = {}

        self.default_settings = {
            "theme": "dark",
            "font_size": 11,
            "default_model_type": "local",
            "max_history": 50,
            "auto_save": True,
            "window_width": 1400,
            "window_height": 900,
            "model_configs": {
                "local": {
                    "context_length": 4096,
                    "max_tokens": 2048,
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "top_k": 40,
                    "repeat_penalty": 1.1,
                    "threads": max(1, (os.cpu_count() or 4) - 2),
                    "gpu_layers": -1   # -1 = full GPU offload
                },
                "openai": {
                    "model": "gpt-4o",
                    "temperature": 0.7,
                    "max_tokens": 2048,
                },
                "anthropic": {
                    "model": "claude-sonnet-4-5",
                    "temperature": 0.7,
                    "max_tokens": 2048,
                },
                "gemini": {
                    "model": "gemini-1.5-pro",
                    "temperature": 0.7,
                    "max_tokens": 2048,
                    "top_p": 0.95,
                    "top_k": 40,
                }
            }
        }

    def load(self):
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    loaded = json.load(f)
                    self.settings = {**self.default_settings, **loaded}
            except Exception as e:
                print(f"Error loading settings: {e}")
                self.settings = self.default_settings.copy()
        else:
            self.settings = self.default_settings.copy()
            self.save()

        if self.keys_file.exists():
            try:
                with open(self.keys_file, 'r') as f:
                    self.api_keys = json.load(f)
            except Exception as e:
                print(f"Error loading API keys: {e}")
                self.api_keys = {}

    def save(self):
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def save_keys(self):
        try:
            with open(self.keys_file, 'w') as f:
                json.dump(self.api_keys, f, indent=2)
        except Exception as e:
            print(f"Error saving API keys: {e}")

    def get(self, key: str, default=None):
        return self.settings.get(key, default)

    def set(self, key: str, value: Any):
        self.settings[key] = value
        self.save()

    def get_model_config(self, model_type: str = None) -> Dict[str, Any]:
        if model_type is None:
            model_type = self.get("default_model_type", "local")
        return self.settings.get("model_configs", {}).get(model_type, {})

    def set_model_config(self, model_type: str, config: Dict[str, Any]):
        if "model_configs" not in self.settings:
            self.settings["model_configs"] = {}
        self.settings["model_configs"][model_type] = config
        self.save()

    def get_api_key(self, provider: str) -> Optional[str]:
        return self.api_keys.get(provider)

    def set_api_key(self, provider: str, key: str):
        self.api_keys[provider] = key
        self.save_keys()

    def delete_api_key(self, provider: str):
        if provider in self.api_keys:
            del self.api_keys[provider]
            self.save_keys()
