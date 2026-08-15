"""
Model loading: llama-cpp-python (offline) + API (online)
Supports: Local GGUF, OpenAI, Anthropic, Gemini

All API packages are imported LAZILY (only when actually used).
The app works fully offline when using a local GGUF model.
"""

import os
from typing import Dict, Any, Callable, Optional
from pathlib import Path


class ModelManager:
    """Manages AI model loading and inference"""

    def __init__(self, config):
        self.config = config
        self.model = None
        self.model_type = None
        self.model_name = None
        self.model_path = None

        self.openai_client = None
        self.anthropic_client = None
        self.gemini_model_obj = None

    def get_available_local_models(self) -> list:
        """Scan models/ folder for GGUF files"""
        models_dir = Path("models")
        if not models_dir.exists():
            models_dir.mkdir(exist_ok=True)
            return []
        return list(models_dir.glob("*.gguf"))

    def load_model(self, model_type: str = None, model_path: str = None):
        if model_type is None:
            model_type = self.config.get("default_model_type", "local")
        self.model_type = model_type

        if model_type == "local":
            return self._load_local_model(model_path)
        elif model_type == "openai":
            return self._load_openai_model()
        elif model_type == "anthropic":
            return self._load_anthropic_model()
        elif model_type == "gemini":
            return self._load_gemini_model()
        else:
            raise ValueError(f"Unknown model type: {model_type}")

    def _load_local_model(self, model_path: str = None):
        """Load a local GGUF model — works 100% offline"""
        try:
            from llama_cpp import Llama
        except ImportError:
            raise ImportError(
                "llama-cpp-python is not installed.\n"
                "Run install.bat to install it with GPU support."
            )

        if model_path is None:
            gguf_files = self.get_available_local_models()
            if not gguf_files:
                raise FileNotFoundError(
                    "No .gguf model found in models/ folder.\n"
                    "Please place a GGUF model file in the models/ directory."
                )
            model_path = str(gguf_files[0])

        self.model_path = model_path
        print(f"Loading local model: {model_path}")

        model_config = self.config.get_model_config("local")

        self.model = Llama(
            model_path=model_path,
            n_ctx=model_config.get("context_length", 4096),
            n_threads=model_config.get("threads", max(1, (os.cpu_count() or 4) - 2)),
            n_gpu_layers=model_config.get("gpu_layers", -1),
            verbose=False,
            use_mmap=True,
            use_mlock=False,
        )

        self.model_name = Path(model_path).stem
        print(f"Model loaded: {self.model_name}")
        return True

    def _load_openai_model(self):
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("openai not installed. Run: pip install openai")

        api_key = self.config.get_api_key("openai")
        if not api_key:
            raise ValueError("OpenAI API key not set. Add it via the API Keys button.")

        self.openai_client = OpenAI(api_key=api_key)
        self.model_name = self.config.get_model_config("openai").get("model", "gpt-4o")
        self.model = "openai_ready"
        print(f"OpenAI model ready: {self.model_name}")
        return True

    def _load_anthropic_model(self):
        try:
            import anthropic
        except ImportError:
            raise ImportError("anthropic not installed. Run: pip install anthropic")

        api_key = self.config.get_api_key("anthropic")
        if not api_key:
            raise ValueError("Anthropic API key not set. Add it via the API Keys button.")

        self.anthropic_client = anthropic.Anthropic(api_key=api_key)
        self.model_name = self.config.get_model_config("anthropic").get("model", "claude-sonnet-4-5")
        self.model = "anthropic_ready"
        print(f"Anthropic model ready: {self.model_name}")
        return True

    def _load_gemini_model(self):
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError("google-generativeai not installed. Run: pip install google-generativeai")

        api_key = self.config.get_api_key("gemini")
        if not api_key:
            raise ValueError("Gemini API key not set. Add it via the API Keys button.")

        genai.configure(api_key=api_key)
        model_name = self.config.get_model_config("gemini").get("model", "gemini-1.5-pro")
        self.gemini_model_obj = genai.GenerativeModel(model_name)
        self.model_name = model_name
        self.model = "gemini_ready"
        print(f"Gemini model ready: {self.model_name}")
        return True

    def generate(self, prompt: str, params: Dict[str, Any] = None,
                 stream_callback: Callable = None) -> str:
        if self.model is None:
            raise RuntimeError("No model loaded. Please load a model first.")

        if params is None:
            params = self.config.get_model_config(self.model_type)

        if self.model_type == "local":
            return self._generate_local(prompt, params, stream_callback)
        elif self.model_type == "openai":
            return self._generate_openai(prompt, params, stream_callback)
        elif self.model_type == "anthropic":
            return self._generate_anthropic(prompt, params, stream_callback)
        elif self.model_type == "gemini":
            return self._generate_gemini(prompt, params)
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")

    def _generate_local(self, prompt: str, params: Dict[str, Any],
                        stream_callback: Callable = None) -> str:
        if stream_callback:
            full_response = ""
            for chunk in self.model(
                prompt,
                max_tokens=params.get("max_tokens", 2048),
                temperature=params.get("temperature", 0.7),
                top_p=params.get("top_p", 0.95),
                top_k=params.get("top_k", 40),
                repeat_penalty=params.get("repeat_penalty", 1.1),
                stop=["User:", "\nUser:", "Human:"],
                echo=False,
                stream=True,
            ):
                token = chunk["choices"][0]["text"]
                full_response += token
                stream_callback(token)
            return full_response.strip()
        else:
            output = self.model(
                prompt,
                max_tokens=params.get("max_tokens", 2048),
                temperature=params.get("temperature", 0.7),
                top_p=params.get("top_p", 0.95),
                top_k=params.get("top_k", 40),
                repeat_penalty=params.get("repeat_penalty", 1.1),
                stop=["User:", "\nUser:", "Human:"],
                echo=False,
            )
            return output["choices"][0]["text"].strip()

    def _generate_openai(self, prompt: str, params: Dict[str, Any],
                         stream_callback: Callable = None) -> str:
        messages = [
            {"role": "system", "content": "You are ASVault, an AI coding assistant."},
            {"role": "user", "content": prompt}
        ]
        if stream_callback:
            full_response = ""
            with self.openai_client.chat.completions.create(
                model=self.model_name, messages=messages,
                temperature=params.get("temperature", 0.7),
                max_tokens=params.get("max_tokens", 2048),
                stream=True,
            ) as stream:
                for chunk in stream:
                    token = chunk.choices[0].delta.content or ""
                    full_response += token
                    stream_callback(token)
            return full_response.strip()
        else:
            response = self.openai_client.chat.completions.create(
                model=self.model_name, messages=messages,
                temperature=params.get("temperature", 0.7),
                max_tokens=params.get("max_tokens", 2048),
            )
            return response.choices[0].message.content.strip()

    def _generate_anthropic(self, prompt: str, params: Dict[str, Any],
                             stream_callback: Callable = None) -> str:
        if stream_callback:
            full_response = ""
            with self.anthropic_client.messages.stream(
                model=self.model_name,
                max_tokens=params.get("max_tokens", 2048),
                system="You are ASVault, an AI coding assistant.",
                messages=[{"role": "user", "content": prompt}],
            ) as stream:
                for text in stream.text_stream:
                    full_response += text
                    stream_callback(text)
            return full_response.strip()
        else:
            response = self.anthropic_client.messages.create(
                model=self.model_name,
                max_tokens=params.get("max_tokens", 2048),
                system="You are ASVault, an AI coding assistant.",
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text.strip()

    def _generate_gemini(self, prompt: str, params: Dict[str, Any]) -> str:
        response = self.gemini_model_obj.generate_content(
            prompt,
            generation_config={
                "temperature": params.get("temperature", 0.7),
                "max_output_tokens": params.get("max_tokens", 2048),
                "top_p": params.get("top_p", 0.95),
                "top_k": params.get("top_k", 40),
            }
        )
        return response.text.strip()

    def switch_model(self, model_type: str, model_path: str = None):
        self.cleanup()
        self.load_model(model_type, model_path)

    def cleanup(self):
        if self.model_type == "local" and self.model and not isinstance(self.model, str):
            del self.model
        self.model = None
        self.model_type = None
        self.model_name = None
