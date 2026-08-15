"""
create_file, edit_file, read_file, delete_file, search_file, create_folder
"""

import os
import re
from pathlib import Path
from typing import List, Tuple, Optional

class FileIO:
    """Core file operations"""
    
    def __init__(self, config):
        self.config = config
        self.working_directory = Path.cwd()
        
    def set_working_directory(self, path: str):
        """Set the working directory"""
        new_path = Path(path)
        if new_path.exists() and new_path.is_dir():
            self.working_directory = new_path
            return True
        return False
        
    def _resolve_path(self, path: str) -> Path:
        """Resolve path relative to working directory"""
        p = Path(path)
        if not p.is_absolute():
            p = self.working_directory / p
        return p.resolve()
        
    def create_file(self, path: str, content: str = "") -> bool:
        """Create a new file with optional content"""
        try:
            file_path = self._resolve_path(path)
            
            # Create parent directories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write content
            file_path.write_text(content, encoding='utf-8')
            return True
        except Exception as e:
            print(f"Error creating file {path}: {e}")
            return False
            
    def edit_file(self, path: str, search: str, replace: str) -> bool:
        """Edit a file by replacing text"""
        try:
            file_path = self._resolve_path(path)
            
            if not file_path.exists():
                return False
                
            # Read current content
            content = file_path.read_text(encoding='utf-8')
            
            # Perform replacement
            new_content = content.replace(search, replace)
            
            # Write back
            file_path.write_text(new_content, encoding='utf-8')
            return True
        except Exception as e:
            print(f"Error editing file {path}: {e}")
            return False
            
    def read_file(self, path: str) -> Optional[str]:
        """Read and return file content"""
        try:
            file_path = self._resolve_path(path)
            
            if not file_path.exists():
                return None
                
            return file_path.read_text(encoding='utf-8')
        except Exception as e:
            print(f"Error reading file {path}: {e}")
            return None
            
    def delete_file(self, path: str) -> bool:
        """Delete a file"""
        try:
            file_path = self._resolve_path(path)
            
            if file_path.exists() and file_path.is_file():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting file {path}: {e}")
            return False
            
    def search_in_file(self, path: str, pattern: str) -> List[Tuple[int, str]]:
        """Search for pattern in file and return line numbers"""
        results = []
        
        try:
            file_path = self._resolve_path(path)
            
            if not file_path.exists():
                return results
                
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            for i, line in enumerate(lines, 1):
                if pattern in line:
                    results.append((i, line))
        except Exception as e:
            print(f"Error searching file {path}: {e}")
            
        return results
        
    def create_folder(self, path: str) -> bool:
        """Create a new folder"""
        try:
            folder_path = self._resolve_path(path)
            folder_path.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error creating folder {path}: {e}")
            return False
            
    def delete_folder(self, path: str, recursive: bool = False) -> bool:
        """Delete a folder"""
        try:
            folder_path = self._resolve_path(path)
            
            if not folder_path.exists() or not folder_path.is_dir():
                return False
                
            if recursive:
                import shutil
                shutil.rmtree(folder_path)
            else:
                folder_path.rmdir()
                
            return True
        except Exception as e:
            print(f"Error deleting folder {path}: {e}")
            return False
            
    def list_directory(self, path: str = "") -> List[str]:
        """List contents of a directory"""
        try:
            target = self._resolve_path(path) if path else self.working_directory
            
            if not target.exists() or not target.is_dir():
                return []
                
            return [str(item.name) for item in sorted(target.iterdir())]
        except Exception as e:
            print(f"Error listing directory: {e}")
            return []
            
    def move_file(self, source: str, destination: str) -> bool:
        """Move or rename a file"""
        try:
            src_path = self._resolve_path(source)
            dst_path = self._resolve_path(destination)
            
            if not src_path.exists():
                return False
                
            # Create destination directory if needed
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            
            src_path.rename(dst_path)
            return True
        except Exception as e:
            print(f"Error moving file {source} to {destination}: {e}")
            return False
            
    def copy_file(self, source: str, destination: str) -> bool:
        """Copy a file"""
        try:
            import shutil
            src_path = self._resolve_path(source)
            dst_path = self._resolve_path(destination)
            
            if not src_path.exists():
                return False
                
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dst_path)
            return True
        except Exception as e:
            print(f"Error copying file {source} to {destination}: {e}")
            return False