"""
Syntax-highlighted file viewer (right panel)
"""

import tkinter as tk
from tkinter import font
from pathlib import Path
import re

class SyntaxHighlighter:
    """Simple syntax highlighter for common languages"""
    
    # Language patterns
    PATTERNS = {
        'python': {
            'keywords': r'\b(def|class|if|else|elif|for|while|return|import|from|as|try|except|finally|with|lambda|and|or|not|is|None|True|False)\b',
            'strings': r'(["\'])(?:(?=(\\?))\2.)*?\1',
            'comments': r'#.*$',
            'numbers': r'\b\d+\b',
            'functions': r'\b\w+(?=\()',
        },
        'javascript': {
            'keywords': r'\b(function|class|if|else|for|while|return|import|export|const|let|var|new|try|catch|finally|throw|async|await)\b',
            'strings': r'(["\'])(?:(?=(\\?))\2.)*?\1',
            'comments': r'//.*$|/\*.*?\*/',
            'numbers': r'\b\d+\b',
        },
        'html': {
            'tags': r'<[^>]+>',
            'attributes': r'\b\w+(?=\=)',
            'comments': r'<!--.*?-->',
        },
        'css': {
            'selectors': r'[.#][\w-]+|\b\w+(?=\s*\{)',
            'properties': r'[\w-]+(?=\s*:)',
            'comments': r'/\*.*?\*/',
        }
    }
    
    COLORS = {
        'keyword': '#569CD6',
        'string': '#CE9178',
        'comment': '#6A9955',
        'number': '#B5CEA8',
        'function': '#DCDCAA',
        'tag': '#569CD6',
        'attribute': '#9CDCFE',
        'selector': '#D7BA7D',
        'property': '#9CDCFE',
        'default': '#D4D4D4',
    }
    
    @classmethod
    def get_language(cls, filepath: Path) -> str:
        """Detect language from file extension"""
        ext = filepath.suffix.lower()
        mapping = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'javascript',
            '.html': 'html',
            '.htm': 'html',
            '.css': 'css',
            '.json': 'javascript',
            '.md': 'markdown',
        }
        return mapping.get(ext, 'python')
        
    @classmethod
    def highlight(cls, text_widget, filepath: Path):
        """Apply syntax highlighting to text widget"""
        language = cls.get_language(filepath)
        patterns = cls.PATTERNS.get(language, {})
        
        # Clear existing tags
        for tag in text_widget.tag_names():
            if tag not in ('sel', 'sel.first', 'sel.last'):
                text_widget.tag_delete(tag)
                
        # Configure color tags
        for color_name, color_code in cls.COLORS.items():
            text_widget.tag_configure(color_name, foreground=color_code)
            
        # Apply highlighting
        content = text_widget.get("1.0", "end-1c")
        
        for pattern_type, pattern in patterns.items():
            color_tag = pattern_type if pattern_type in cls.COLORS else 'default'
            
            for match in re.finditer(pattern, content, re.MULTILINE | re.DOTALL):
                start_idx = f"1.0 + {match.start()} chars"
                end_idx = f"1.0 + {match.end()} chars"
                text_widget.tag_add(color_tag, start_idx, end_idx)
                
        # Highlight line numbers (simplified)
        text_widget.tag_configure('line_number', foreground='#858585')
        
        lines = content.split('\n')
        for i in range(1, len(lines) + 1):
            line_start = f"{i}.0"
            line_end = f"{i}.end"
            text_widget.tag_add('line_number', line_start, line_end)

class CodeViewer:
    """Code viewer with syntax highlighting"""
    
    def __init__(self, parent_widget):
        self.parent = parent_widget
        self.current_file = None
        self.setup_viewer()
        
    def setup_viewer(self):
        """Setup the code viewer with scrollbars"""
        # Create frame
        self.frame = tk.Frame(self.parent)
        self.frame.pack(fill='both', expand=True)
        
        # Create text widget
        self.text_widget = tk.Text(
            self.frame,
            wrap='none',
            font=('Consolas', 11),
            bg='#1E1E1E',
            fg='#D4D4D4',
            insertbackground='white',
            selectbackground='#264F78',
            relief='flat',
            padx=10,
            pady=10
        )
        
        # Add scrollbars
        v_scrollbar = tk.Scrollbar(self.frame, orient='vertical', command=self.text_widget.yview)
        h_scrollbar = tk.Scrollbar(self.frame, orient='horizontal', command=self.text_widget.xview)
        
        self.text_widget.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.text_widget.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        
        # Bind events
        self.text_widget.bind('<Control-=>', self.zoom_in)
        self.text_widget.bind('<Control-minus>', self.zoom_out)
        self.text_widget.bind('<Control-0>', self.reset_zoom)
        
        self.current_font_size = 11
        
    def load_file(self, filepath: Path):
        """Load and display a file with syntax highlighting"""
        try:
            content = filepath.read_text(encoding='utf-8')
            self.current_file = filepath
            
            # Update text widget
            self.text_widget.delete('1.0', 'end')
            self.text_widget.insert('1.0', content)
            
            # Apply syntax highlighting
            SyntaxHighlighter.highlight(self.text_widget, filepath)
            
            return True
        except Exception as e:
            self.text_widget.delete('1.0', 'end')
            self.text_widget.insert('1.0', f"Error loading file: {str(e)}")
            return False
            
    def save_file(self):
        """Save current file"""
        if self.current_file:
            content = self.text_widget.get('1.0', 'end-1c')
            self.current_file.write_text(content, encoding='utf-8')
            return True
        return False
        
    def zoom_in(self, event=None):
        """Increase font size"""
        self.current_font_size += 1
        current_font = font.Font(font=self.text_widget['font'])
        current_font.config(size=self.current_font_size)
        self.text_widget['font'] = current_font
        return 'break'
        
    def zoom_out(self, event=None):
        """Decrease font size"""
        if self.current_font_size > 8:
            self.current_font_size -= 1
            current_font = font.Font(font=self.text_widget['font'])
            current_font.config(size=self.current_font_size)
            self.text_widget['font'] = current_font
        return 'break'
        
    def reset_zoom(self, event=None):
        """Reset font size to default"""
        self.current_font_size = 11
        current_font = font.Font(font=self.text_widget['font'])
        current_font.config(size=self.current_font_size)
        self.text_widget['font'] = current_font
        return 'break'
        
    def clear(self):
        """Clear the viewer"""
        self.text_widget.delete('1.0', 'end')
        self.current_file = None