"""
File/folder browser, context selection, directory search
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import fnmatch

class FileManager:
    """Manages file browsing and searching"""
    
    def __init__(self, config):
        self.config = config
        self.current_directory = Path.cwd()
        self.selected_files: List[Path] = []
        
    def set_directory(self, path: str):
        """Set the current working directory"""
        new_path = Path(path)
        if new_path.exists() and new_path.is_dir():
            self.current_directory = new_path
            return True
        return False
        
    def get_directory_contents(self, path: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get contents of a directory"""
        target = Path(path) if path else self.current_directory
        
        if not target.exists() or not target.is_dir():
            return []
            
        contents = []
        
        try:
            for item in sorted(target.iterdir()):
                contents.append({
                    "name": item.name,
                    "path": str(item),
                    "is_dir": item.is_dir(),
                    "size": item.stat().st_size if item.is_file() else 0,
                    "modified": item.stat().st_mtime
                })
        except PermissionError:
            pass
            
        return contents
        
    def search_files(self, pattern: str, directory: Optional[str] = None) -> List[Path]:
        """Search for files matching pattern"""
        target = Path(directory) if directory else self.current_directory
        matches = []
        
        try:
            for root, dirs, files in os.walk(target):
                # Skip hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for file in files:
                    if fnmatch.fnmatch(file, pattern):
                        matches.append(Path(root) / file)
        except PermissionError:
            pass
            
        return matches
        
    def search_content(self, pattern: str, directory: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for content in files"""
        target = Path(directory) if directory else self.current_directory
        results = []
        
        # Common text file extensions
        text_extensions = {'.py', '.txt', '.md', '.json', '.yaml', '.yml', 
                          '.js', '.html', '.css', '.cpp', '.c', '.h'}
        
        try:
            for root, dirs, files in os.walk(target):
                # Skip hidden directories and common ignore patterns
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in {'node_modules', '__pycache__'}]
                
                for file in files:
                    file_path = Path(root) / file
                    
                    # Check if it's a text file
                    if file_path.suffix in text_extensions:
                        try:
                            content = file_path.read_text(encoding='utf-8')
                            if pattern.lower() in content.lower():
                                # Find line numbers
                                lines = content.split('\n')
                                matches = []
                                for i, line in enumerate(lines, 1):
                                    if pattern.lower() in line.lower():
                                        matches.append({
                                            "line_num": i,
                                            "line": line.strip()
                                        })
                                        
                                results.append({
                                    "file": str(file_path),
                                    "matches": matches
                                })
                        except (UnicodeDecodeError, PermissionError):
                            continue
        except PermissionError:
            pass
            
        return results
        
    def add_to_context(self, file_path: str):
        """Add a file to the current context"""
        path = Path(file_path)
        if path.exists() and path.is_file():
            if path not in self.selected_files:
                self.selected_files.append(path)
                return True
        return False
        
    def remove_from_context(self, file_path: str):
        """Remove a file from context"""
        path = Path(file_path)
        if path in self.selected_files:
            self.selected_files.remove(path)
            return True
        return False
        
    def get_context_files(self) -> List[Path]:
        """Get list of files in current context"""
        return self.selected_files.copy()
        
    def get_context_content(self) -> str:
        """Get concatenated content of all context files"""
        content_parts = []
        
        for file_path in self.selected_files:
            try:
                content = file_path.read_text(encoding='utf-8')
                content_parts.append(f"=== {file_path.name} ===\n{content}\n")
            except Exception:
                content_parts.append(f"=== {file_path.name} ===\n[Error reading file]\n")
                
        return "\n".join(content_parts)
        
    def clear_context(self):
        """Clear all files from context"""
        self.selected_files.clear()
        
    def get_file_tree(self, directory: Optional[str] = None, indent: int = 0) -> str:
        """Generate a tree representation of directory structure"""
        target = Path(directory) if directory else self.current_directory
        tree_lines = []
        
        try:
            items = sorted(target.iterdir())
            for i, item in enumerate(items):
                is_last = i == len(items) - 1
                prefix = "    " * indent + ("└── " if is_last else "├── ")
                
                if item.is_dir():
                    tree_lines.append(f"{prefix}{item.name}/")
                    tree_lines.append(self.get_file_tree(str(item), indent + 1))
                else:
                    tree_lines.append(f"{prefix}{item.name}")
        except PermissionError:
            tree_lines.append("    " * indent + "[Permission denied]")
            
        return "\n".join(tree_lines)