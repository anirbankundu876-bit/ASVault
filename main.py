#!/usr/bin/env python3
"""
ASVault v2 - Agentic Coding Assistant
Main entry point - initialises all modules
"""

import sys
import os
import threading
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui import ASVaultUI
from config import Config
from model_manager import ModelManager
from chat_engine import ChatEngine
from action_executor import ActionExecutor
from file_manager import FileManager
from file_io import FileIO
from terminal import EmbeddedTerminal


class ASVaultApp:
    """Main application class that orchestrates all modules"""

    def __init__(self):
        print("Initializing ASVault v2...")

        # Load configuration
        self.config = Config()
        self.config.load()

        # Initialize modules
        self.model_manager = ModelManager(self.config)
        self.chat_engine = ChatEngine(self.config)
        self.action_executor = ActionExecutor(self.config)
        self.file_manager = FileManager(self.config)
        self.file_io = FileIO(self.config)
        self.terminal = EmbeddedTerminal()

        self.ui = None
        self.model_loaded = False

    def initialize_ui(self):
        """Create and setup the UI"""
        self.ui = ASVaultUI(self)
        return self.ui

    def load_model_background(self):
        """Load the AI model in a background thread"""
        def load():
            try:
                self.model_manager.load_model()
                self.model_loaded = True
                if self.ui:
                    self.ui.root.after(0, lambda: self.ui.update_model_status(
                        f"Ready — {self.model_manager.model_name}", "green"
                    ))
            except Exception as e:
                if self.ui:
                    self.ui.root.after(0, lambda: self.ui.update_model_status(
                        f"Error: {str(e)}", "red"
                    ))

        threading.Thread(target=load, daemon=True).start()

    def send_message(self, message: str, stream_callback=None):
        """Process user message through chat engine"""
        self.chat_engine.add_user_message(message)

        if not self.model_loaded:
            return "Model is still loading. Please wait..."

        try:
            response = self.model_manager.generate(
                self.chat_engine.build_prompt(),
                self.config.get_model_config(),
                stream_callback=stream_callback
            )

            # Parse and execute actions
            actions = self.chat_engine.parse_tags(response)
            action_results = []
            for action in actions:
                result = self.action_executor.execute(action)
                action_results.append(result)

            # Clean response (remove action tags)
            clean_response = self.chat_engine.clean_response(response)

            # Append action results to response
            if action_results:
                clean_response += "\n\n**Actions executed:**\n"
                for r in action_results:
                    if r["success"]:
                        clean_response += f"✅ {r['result']}\n"
                    else:
                        clean_response += f"❌ {r['error']}\n"

            self.chat_engine.add_assistant_message(clean_response)
            return clean_response

        except Exception as e:
            return f"Error generating response: {str(e)}"

    def run(self):
        """Start the application"""
        self.initialize_ui()
        self.load_model_background()
        self.ui.root.mainloop()


def main():
    app = ASVaultApp()
    app.run()


if __name__ == "__main__":
    main()
