"""
Jupyter Raw Cell Widget Executor
Handles raw text cells imported from Jupyter notebooks
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../core'))
from base_widget import WidgetExecutor
from typing import Dict, Any


class JupyterRawWidget(WidgetExecutor):
    """Jupyter raw cell widget for unformatted text content"""
    
    def _execute_impl(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute raw cell rendering"""
        
        source = validated_input['source']
        format_type = validated_input.get('format', 'text')
        
        # Apply formatting based on type
        rendered_content = self._apply_format(source, format_type)
        
        result = {
            'rendered_content': rendered_content,
            'format_applied': format_type,
            'source_length': len(source),
            'line_count': len(source.split('\n'))
        }
        
        # Add Jupyter metadata if available
        if hasattr(self, 'jupyter_metadata'):
            result['jupyter_metadata'] = self.jupyter_metadata
            
        return result
    
    def _apply_format(self, source: str, format_type: str) -> str:
        """Apply formatting to raw content based on type"""
        
        if format_type == 'html':
            return self._format_as_html(source)
        elif format_type == 'latex':
            return self._format_as_latex(source)
        elif format_type == 'restructuredtext':
            return self._format_as_rst(source)
        elif format_type == 'asciidoc':
            return self._format_as_asciidoc(source)
        else:  # text
            return self._format_as_text(source)
    
    def _format_as_html(self, source: str) -> str:
        """Format raw content as HTML"""
        # Basic HTML rendering - in production, sanitize for security
        return f'<div class="raw-html-content">{source}</div>'
    
    def _format_as_latex(self, source: str) -> str:
        """Format raw content as LaTeX"""
        # Wrap in LaTeX display container
        return f'<div class="raw-latex-content">$$\n{source}\n$$</div>'
    
    def _format_as_rst(self, source: str) -> str:
        """Format raw content as reStructuredText"""
        # Basic RST formatting (simplified)
        lines = source.split('\n')
        formatted_lines = []
        
        for line in lines:
            # Convert RST headers (simplified)
            if line.strip() and len(lines) > lines.index(line) + 1:
                next_line = lines[lines.index(line) + 1]
                if next_line.strip() and all(c in '=-~^' for c in next_line.strip()):
                    # This is a header
                    level = {'=': 1, '-': 2, '~': 3, '^': 4}.get(next_line.strip()[0], 2)
                    formatted_lines.append(f'<h{level}>{self._escape_html(line.strip())}</h{level}>')
                    continue
            
            # Convert emphasis (simplified)
            line = self._escape_html(line)
            line = line.replace('**', '<strong>').replace('**', '</strong>')
            line = line.replace('*', '<em>').replace('*', '</em>')
            
            formatted_lines.append(line)
        
        return f'<div class="raw-rst-content">{"<br>".join(formatted_lines)}</div>'
    
    def _format_as_asciidoc(self, source: str) -> str:
        """Format raw content as AsciiDoc"""
        # Very basic AsciiDoc formatting
        lines = source.split('\n')
        formatted_lines = []
        
        for line in lines:
            # Convert headers
            if line.startswith('= '):
                formatted_lines.append(f'<h1>{self._escape_html(line[2:])}</h1>')
            elif line.startswith('== '):
                formatted_lines.append(f'<h2>{self._escape_html(line[3:])}</h2>')
            elif line.startswith('=== '):
                formatted_lines.append(f'<h3>{self._escape_html(line[4:])}</h3>')
            else:
                # Convert emphasis
                line = self._escape_html(line)
                line = line.replace('*', '<strong>').replace('*', '</strong>')
                line = line.replace('_', '<em>').replace('_', '</em>')
                formatted_lines.append(line)
        
        return f'<div class="raw-asciidoc-content">{"<br>".join(formatted_lines)}</div>'
    
    def _format_as_text(self, source: str) -> str:
        """Format raw content as plain text"""
        return f'<pre class="raw-text-content">{self._escape_html(source)}</pre>'
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML characters"""
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&#x27;'))
    
    def set_jupyter_metadata(self, metadata: Dict):
        """Set Jupyter cell metadata"""
        self.jupyter_metadata = metadata