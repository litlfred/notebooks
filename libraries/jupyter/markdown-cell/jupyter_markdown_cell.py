"""
Jupyter Markdown Cell Widget Executor
Handles markdown cells imported from Jupyter notebooks with enhanced rendering
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../core'))
from base_widget import WidgetExecutor
import re
import time


class JupyterMarkdownWidget(WidgetExecutor):
    """Jupyter markdown cell widget - extends sticky note functionality"""
    
    def _execute_impl(self, validated_input):
        """Execute markdown rendering with Jupyter-specific enhancements"""
        
        content = validated_input['content']
        render_latex = validated_input.get('render_latex', True)
        
        # Process Jupyter markdown extensions
        enhanced_content = self._process_jupyter_markdown(content)
        
        # Render markdown to HTML
        rendered_html = self._render_markdown(enhanced_content, render_latex)
        
        result = {
            'rendered_html': rendered_html,
            'variables_used': self._find_variables(enhanced_content),
            'word_count': len(enhanced_content.split()),
            'character_count': len(enhanced_content)
        }
        
        # Add Jupyter-specific metadata to output
        if hasattr(self, 'jupyter_metadata'):
            result['jupyter_metadata'] = self.jupyter_metadata
        
        return result
    
    def _process_jupyter_markdown(self, content):
        """Process Jupyter-specific markdown features"""
        
        # Handle Jupyter cell references (e.g., [Cell 2] -> <cell-ref>2</cell-ref>)
        content = re.sub(
            r'\[Cell\s+(\d+)\]', 
            r'<span class="cell-reference">Cell \1</span>', 
            content
        )
        
        # Handle Jupyter magic commands in markdown (render as code)
        content = re.sub(
            r'(^|\n)(%%?\w+.*?)(\n|$)',
            r'\1```\n\2\n```\3',
            content,
            flags=re.MULTILINE
        )
        
        # Handle attachment references
        content = re.sub(
            r'attachment:([a-zA-Z0-9._-]+)',
            r'<span class="attachment-ref">[Attachment: \1]</span>',
            content
        )
        
        return content
    
    def set_jupyter_metadata(self, metadata):
        """Set Jupyter cell metadata"""
        self.jupyter_metadata = metadata
    
    def _find_variables(self, content: str) -> List[str]:
        """Find variable references in content like {{variable_name}}"""
        pattern = r'\{\{([^}]+)\}\}'
        variables = re.findall(pattern, content)
        return [var.strip() for var in variables]
    
    def _render_markdown(self, content: str, render_latex: bool) -> str:
        """Simple markdown to HTML conversion"""
        html = content
        
        # Headers
        html = re.sub(r'^# (.*$)', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.*$)', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^### (.*$)', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        
        # Bold and italic
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
        
        # Code blocks
        html = re.sub(r'```(.*?)```', r'<pre><code>\1</code></pre>', html, flags=re.DOTALL)
        html = re.sub(r'`(.*?)`', r'<code>\1</code>', html)
        
        # Line breaks
        html = html.replace('\n', '<br>')
        
        # LaTeX rendering placeholder
        if render_latex:
            html = re.sub(r'\$(.*?)\$', r'<span class="latex">\1</span>', html)
            html = re.sub(r'\$\$(.*?)\$\$', r'<div class="latex-block">\1</div>', html, flags=re.DOTALL)
        
        return html