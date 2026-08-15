"""
Embedded terminal widget (bottom panel, no internet)
"""

import subprocess
import threading
import queue
import os
import sys
from typing import Dict, Any

class TerminalExecutor:
    """Execute terminal commands and capture output"""
    
    def __init__(self):
        self.current_directory = os.getcwd()
        
    def execute(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """Execute a command and return output"""
        try:
            # Run command
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.current_directory,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            # Combine stdout and stderr
            output = result.stdout
            if result.stderr:
                output += result.stderr
                
            # Update working directory if cd command
            if command.strip().startswith('cd '):
                try:
                    new_dir = command.strip()[3:].strip()
                    if new_dir:
                        os.chdir(new_dir)
                        self.current_directory = os.getcwd()
                except Exception:
                    pass
                    
            return {
                "success": result.returncode == 0,
                "output": output if output else "[Command completed with no output]",
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": f"Command timed out after {timeout} seconds"
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": str(e)
            }
            
    def set_directory(self, directory: str):
        """Set the working directory"""
        if os.path.exists(directory) and os.path.isdir(directory):
            self.current_directory = directory
            os.chdir(directory)
            return True
        return False

class EmbeddedTerminal:
    """Embedded terminal widget for the UI"""
    
    def __init__(self):
        self.widget = None
        self.executor = TerminalExecutor()
        self.history = []
        self.history_index = -1
        
    def set_widget(self, text_widget):
        """Set the text widget for terminal display"""
        self.widget = text_widget
        
        # Configure widget for terminal
        self.widget.configure(state='normal')
        self.widget.delete('1.0', 'end')
        
        # Welcome message
        self.write_line("ASVault Terminal - Local command execution")
        self.write_line(f"Working directory: {os.getcwd()}")
        self.write_line("Type commands and press Enter to execute")
        self.write_line("-" * 60)
        self.write_prompt()
        
        # Bind enter key
        self.widget.bind('<Return>', self.on_enter)
        self.widget.bind('<Up>', self.on_up)
        self.widget.bind('<Down>', self.on_down)
        
    def write_line(self, text: str):
        """Write a line to the terminal"""
        if self.widget:
            self.widget.insert('end', text + '\n')
            self.widget.see('end')
            
    def write(self, text: str):
        """Write text to terminal"""
        if self.widget:
            self.widget.insert('end', text)
            self.widget.see('end')
            
    def write_prompt(self):
        """Write the command prompt"""
        self.write(f"\n{os.getcwd()}> ")
        
    def get_current_line(self) -> str:
        """Get the current command line"""
        if not self.widget:
            return ""
            
        # Get the last line
        last_line_start = self.widget.index('end-2c linestart')
        last_line = self.widget.get(last_line_start, 'end-2c')
        
        # Remove prompt if present
        if '> ' in last_line:
            parts = last_line.split('> ', 1)
            if len(parts) > 1:
                return parts[1]
        return last_line
        
    def on_enter(self, event):
        """Handle Enter key press"""
        if not self.widget:
            return 'break'
            
        command = self.get_current_line().strip()
        
        if command:
            # Add to history
            self.history.append(command)
            self.history_index = len(self.history)
            
            # Execute command
            self.write('\n')
            result = self.executor.execute(command)
            
            # Display output
            if result['success']:
                self.write_line(result['output'])
            else:
                self.write_line(f"Error: {result.get('error', 'Command failed')}")
                
        # Write new prompt
        self.write_prompt()
        
        return 'break'
        
    def on_up(self, event):
        """Navigate up in command history"""
        if not self.widget:
            return 'break'
            
        if self.history_index > 0:
            self.history_index -= 1
            self.replace_current_line(self.history[self.history_index])
        return 'break'
        
    def on_down(self, event):
        """Navigate down in command history"""
        if not self.widget:
            return 'break'
            
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.replace_current_line(self.history[self.history_index])
        elif self.history_index == len(self.history) - 1:
            self.history_index = len(self.history)
            self.replace_current_line('')
        return 'break'
        
    def replace_current_line(self, new_text: str):
        """Replace the current command line"""
        if not self.widget:
            return
            
        # Get line start
        line_start = self.widget.index('end-2c linestart')
        line_end = self.widget.index('end-2c')
        
        # Get prompt part
        prompt = self.widget.get(line_start, line_end)
        if '> ' in prompt:
            prompt = prompt.split('> ')[0] + '> '
        else:
            prompt = ''
            
        # Replace line
        self.widget.delete(line_start, line_end)
        self.widget.insert(line_start, prompt + new_text)
        self.widget.see('end')
        
    def clear(self):
        """Clear the terminal"""
        if self.widget:
            self.widget.delete('1.0', 'end')
            self.write_line("Terminal cleared")
            self.write_prompt()