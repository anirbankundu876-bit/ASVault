"""
Message history, prompt building, tag parsing
"""

import re
from typing import List, Dict, Any
from datetime import datetime


class ChatEngine:
    """Manages conversation history and parses AI responses"""

    def __init__(self, config):
        self.config = config
        self.messages: List[Dict[str, str]] = []
        self.max_history = config.get("max_history", 50)

        self.system_prompt = """You are ASVault, a powerful AI coding assistant running locally on the user's machine.
You have full access to the user's files and can perform actions using XML tags.

Available actions:
  <create_file path="relative/path.py">file content here</create_file>
  <edit_file path="relative/path.py">search_text->replacement_text</edit_file>
  <read_file path="relative/path.py"/>
  <delete_file path="relative/path.py"/>
  <search_file path="relative/path.py" pattern="search term"/>
  <create_folder path="relative/folder"/>
  <run_command>command here</run_command>

Rules:
- Always explain what you are about to do BEFORE using action tags.
- You can combine multiple actions in one response.
- Use relative paths unless the user specifies absolute paths.
- For run_command: only use local commands. Never attempt to access the internet via terminal.
- Be concise and helpful."""

        self.messages.append({
            "role": "system",
            "content": self.system_prompt,
            "timestamp": datetime.now().isoformat()
        })

    def add_user_message(self, content: str):
        self.messages.append({
            "role": "user",
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self._trim_history()

    def add_assistant_message(self, content: str):
        self.messages.append({
            "role": "assistant",
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

    def _trim_history(self):
        if len(self.messages) > self.max_history + 1:  # +1 for system
            system = [m for m in self.messages if m["role"] == "system"]
            others = [m for m in self.messages if m["role"] != "system"]
            self.messages = system + others[-self.max_history:]

    def build_prompt(self) -> str:
        parts = []
        for msg in self.messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                parts.append(f"System: {content}\n\n")
            elif role == "user":
                parts.append(f"User: {content}\n")
            elif role == "assistant":
                parts.append(f"Assistant: {content}\n\n")
        parts.append("Assistant: ")
        return "".join(parts)

    def parse_tags(self, text: str) -> List[Dict[str, Any]]:
        """Parse XML-like action tags from AI response"""
        actions = []

        patterns = {
            "create_file":   r'<create_file\s+path=["\']([^"\']+)["\']>(.*?)</create_file>',
            "edit_file":     r'<edit_file\s+path=["\']([^"\']+)["\']>(.*?)</edit_file>',
            "read_file":     r'<read_file\s+path=["\']([^"\']+)["\']\s*/>',
            "delete_file":   r'<delete_file\s+path=["\']([^"\']+)["\']\s*/>',
            "search_file":   r'<search_file\s+path=["\']([^"\']+)["\']\s+pattern=["\']([^"\']+)["\']\s*/>',
            "create_folder": r'<create_folder\s+path=["\']([^"\']+)["\']\s*/>',
            "run_command":   r'<run_command>(.*?)</run_command>',
        }

        for action_type, pattern in patterns.items():
            for match in re.findall(pattern, text, re.DOTALL):
                action = {"type": action_type}
                if action_type in ("create_file", "edit_file"):
                    action["path"], action["content"] = match
                elif action_type in ("read_file", "delete_file", "create_folder"):
                    action["path"] = match
                elif action_type == "search_file":
                    action["path"], action["pattern"] = match
                elif action_type == "run_command":
                    action["command"] = match
                actions.append(action)

        return actions

    def clean_response(self, text: str) -> str:
        """Remove action tags from response, keep surrounding explanation"""
        # Remove full tags with content
        cleaned = re.sub(
            r'<(create_file|edit_file|run_command)[^>]*>.*?</\1>',
            '', text, flags=re.DOTALL
        )
        # Remove self-closing tags
        cleaned = re.sub(r'<[^>]+/>', '', cleaned)
        # Clean up extra blank lines
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        return cleaned.strip()

    def clear_history(self):
        """Clear chat history, keep system prompt"""
        self.messages = [m for m in self.messages if m["role"] == "system"]

    def export_history(self, filepath: str):
        with open(filepath, 'w', encoding='utf-8') as f:
            for msg in self.messages:
                f.write(f"[{msg['timestamp']}] {msg['role'].upper()}:\n{msg['content']}\n")
                f.write("-" * 80 + "\n")
