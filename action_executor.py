"""
Dispatches parsed AI XML tags to correct handler
"""

import os
import subprocess
from pathlib import Path
from typing import Dict, Any
from file_io import FileIO
from terminal import TerminalExecutor

class ActionExecutor:
    """Executes actions parsed from AI responses"""
    
    def __init__(self, config):
        self.config = config
        self.file_io = FileIO(config)
        self.terminal = TerminalExecutor()
        self.action_handlers = {
            "create_file": self.handle_create_file,
            "edit_file": self.handle_edit_file,
            "read_file": self.handle_read_file,
            "delete_file": self.handle_delete_file,
            "search_file": self.handle_search_file,
            "create_folder": self.handle_create_folder,
            "run_command": self.handle_run_command,
        }
        
    def execute(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an action and return result"""
        action_type = action.get("type")
        
        if action_type in self.action_handlers:
            try:
                result = self.action_handlers[action_type](action)
                return {"success": True, "result": result}
            except Exception as e:
                return {"success": False, "error": str(e)}
        else:
            return {"success": False, "error": f"Unknown action type: {action_type}"}
            
    def handle_create_file(self, action: Dict[str, Any]) -> str:
        """Handle file creation action"""
        path = action.get("path")
        content = action.get("content", "")
        
        if not path:
            raise ValueError("No path specified for create_file")
            
        success = self.file_io.create_file(path, content)
        if success:
            return f"Created file: {path}"
        else:
            raise Exception(f"Failed to create file: {path}")
            
    def handle_edit_file(self, action: Dict[str, Any]) -> str:
        """Handle file editing action"""
        path = action.get("path")
        edit_content = action.get("content", "")
        
        if not path:
            raise ValueError("No path specified for edit_file")
            
        # Parse search/replace format
        if "->" in edit_content:
            search, replace = edit_content.split("->", 1)
            success = self.file_io.edit_file(path, search.strip(), replace.strip())
        else:
            # If no ->, replace entire file
            success = self.file_io.create_file(path, edit_content)
            
        if success:
            return f"Edited file: {path}"
        else:
            raise Exception(f"Failed to edit file: {path}")
            
    def handle_read_file(self, action: Dict[str, Any]) -> str:
        """Handle file reading action"""
        path = action.get("path")
        
        if not path:
            raise ValueError("No path specified for read_file")
            
        content = self.file_io.read_file(path)
        if content is not None:
            return f"Content of {path}:\n```\n{content}\n```"
        else:
            raise Exception(f"Failed to read file: {path}")
            
    def handle_delete_file(self, action: Dict[str, Any]) -> str:
        """Handle file deletion action"""
        path = action.get("path")
        
        if not path:
            raise ValueError("No path specified for delete_file")
            
        success = self.file_io.delete_file(path)
        if success:
            return f"Deleted file: {path}"
        else:
            raise Exception(f"Failed to delete file: {path}")
            
    def handle_search_file(self, action: Dict[str, Any]) -> str:
        """Handle file search action"""
        path = action.get("path")
        pattern = action.get("pattern")
        
        if not path or not pattern:
            raise ValueError("Path and pattern required for search_file")
            
        results = self.file_io.search_in_file(path, pattern)
        
        if results:
            result_text = f"Found '{pattern}' in {path}:\n"
            for line_num, line in results:
                result_text += f"  Line {line_num}: {line.strip()}\n"
            return result_text
        else:
            return f"No matches found for '{pattern}' in {path}"
            
    def handle_create_folder(self, action: Dict[str, Any]) -> str:
        """Handle folder creation action"""
        path = action.get("path")
        
        if not path:
            raise ValueError("No path specified for create_folder")
            
        success = self.file_io.create_folder(path)
        if success:
            return f"Created folder: {path}"
        else:
            raise Exception(f"Failed to create folder: {path}")
            
    def handle_run_command(self, action: Dict[str, Any]) -> str:
        """Handle terminal command execution"""
        command = action.get("command")
        
        if not command:
            raise ValueError("No command specified for run_command")
            
        result = self.terminal.execute(command)
        
        if result["success"]:
            return f"Command output:\n{result['output']}"
        else:
            return f"Command failed:\n{result['error']}"