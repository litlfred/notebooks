"""
Jupyter Code Cell Widget Executor
Handles code cells imported from Jupyter notebooks with output rendering
"""

import re
import json
import base64
from typing import Dict, Any, List
from .widget_executor import WidgetExecutor


class JupyterCodeWidget(WidgetExecutor):
    """Jupyter code cell widget with execution and rich output display"""
    
    def _execute_impl(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute code cell with output rendering"""
        
        source = validated_input['source']
        language = validated_input.get('language', 'python')
        
        # For now, we don't execute the code but display it with preserved outputs
        # In a full implementation, this would integrate with kernel execution
        
        result = {
            'source_display': self._format_source_code(source, language),
            'language': language,
            'execution_status': 'display_only',
            'message': 'Code display only - execution not implemented in this demo'
        }
        
        # If we have jupyter metadata with outputs, display them
        if hasattr(self, 'jupyter_outputs'):
            result['outputs'] = self._render_jupyter_outputs(self.jupyter_outputs)
            result['execution_count'] = getattr(self, 'execution_count', None)
        
        if hasattr(self, 'jupyter_metadata'):
            result['jupyter_metadata'] = self.jupyter_metadata
            
        return result
    
    def _format_source_code(self, source: str, language: str) -> str:
        """Format source code for display with syntax highlighting"""
        
        # Basic syntax highlighting with HTML
        if language == 'python':
            return self._highlight_python(source)
        else:
            return f'<pre class="code-block language-{language}"><code>{self._escape_html(source)}</code></pre>'
    
    def _highlight_python(self, code: str) -> str:
        """Basic Python syntax highlighting"""
        
        # Escape HTML
        code = self._escape_html(code)
        
        # Highlight keywords
        keywords = ['def', 'class', 'if', 'else', 'elif', 'for', 'while', 'try', 'except', 
                   'import', 'from', 'return', 'yield', 'with', 'as', 'lambda', 'print']
        
        for keyword in keywords:
            code = re.sub(
                f'\\b{keyword}\\b', 
                f'<span class="keyword">{keyword}</span>', 
                code
            )
        
        # Highlight strings
        code = re.sub(
            r'(["\'])([^"\']*)\1', 
            r'<span class="string">\1\2\1</span>', 
            code
        )
        
        # Highlight comments
        code = re.sub(
            r'(#.*$)', 
            r'<span class="comment">\1</span>', 
            code, 
            flags=re.MULTILINE
        )
        
        return f'<pre class="code-block python"><code>{code}</code></pre>'
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML characters"""
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&#x27;'))
    
    def _render_jupyter_outputs(self, outputs: List[Dict]) -> List[Dict]:
        """Render Jupyter notebook outputs with proper MIME type handling"""
        
        rendered_outputs = []
        
        for output in outputs:
            rendered = {
                'output_type': output['output_type'],
                'rendered_content': ''
            }
            
            if output['output_type'] == 'stream':
                rendered['rendered_content'] = self._render_stream_output(output)
                rendered['stream_name'] = output.get('name', 'stdout')
                
            elif output['output_type'] in ['display_data', 'execute_result']:
                rendered['rendered_content'] = self._render_rich_output(output)
                rendered['execution_count'] = output.get('execution_count', None)
                
            elif output['output_type'] == 'error':
                rendered['rendered_content'] = self._render_error_output(output)
                rendered['error_name'] = output.get('ename', 'Error')
                
            rendered_outputs.append(rendered)
        
        return rendered_outputs
    
    def _render_stream_output(self, output: Dict) -> str:
        """Render stream output (stdout/stderr)"""
        
        text = output.get('text', [])
        if isinstance(text, list):
            text = ''.join(text)
        
        stream_name = output.get('name', 'stdout')
        css_class = 'stream-stdout' if stream_name == 'stdout' else 'stream-stderr'
        
        return f'<pre class="{css_class}">{self._escape_html(text)}</pre>'
    
    def _render_rich_output(self, output: Dict) -> str:
        """Render rich display data with MIME type handling"""
        
        data = output.get('data', {})
        
        # Priority order for MIME types
        mime_priority = [
            'text/html',
            'image/png', 
            'image/jpeg',
            'image/svg+xml',
            'text/latex',
            'application/json',
            'text/plain'
        ]
        
        for mime_type in mime_priority:
            if mime_type in data:
                return self._render_mime_data(mime_type, data[mime_type])
        
        # Fallback to plain text
        return f'<pre class="output-data">{self._escape_html(str(data))}</pre>'
    
    def _render_mime_data(self, mime_type: str, data: Any) -> str:
        """Render data based on MIME type"""
        
        if mime_type == 'text/html':
            # Sanitize HTML for security (basic implementation)
            html_content = ''.join(data) if isinstance(data, list) else data
            # In production, use a proper HTML sanitizer
            return f'<div class="html-output">{html_content}</div>'
            
        elif mime_type in ['image/png', 'image/jpeg']:
            # Handle base64 encoded images
            img_data = ''.join(data) if isinstance(data, list) else data
            return f'<img src="data:{mime_type};base64,{img_data}" class="output-image" />'
            
        elif mime_type == 'image/svg+xml':
            svg_content = ''.join(data) if isinstance(data, list) else data
            return f'<div class="svg-output">{svg_content}</div>'
            
        elif mime_type == 'text/latex':
            latex_content = ''.join(data) if isinstance(data, list) else data
            return f'<div class="latex-output">$${latex_content}$$</div>'
            
        elif mime_type == 'application/json':
            json_content = json.dumps(data, indent=2)
            return f'<pre class="json-output">{self._escape_html(json_content)}</pre>'
            
        else:  # text/plain
            text_content = ''.join(data) if isinstance(data, list) else data
            return f'<pre class="text-output">{self._escape_html(text_content)}</pre>'
    
    def _render_error_output(self, output: Dict) -> str:
        """Render error output with traceback"""
        
        ename = output.get('ename', 'Error')
        evalue = output.get('evalue', '')
        traceback = output.get('traceback', [])
        
        traceback_html = ''.join([
            f'<div class="traceback-line">{self._escape_html(line)}</div>'
            for line in traceback
        ])
        
        return f'''
        <div class="error-output">
            <div class="error-header">
                <span class="error-name">{self._escape_html(ename)}</span>: 
                <span class="error-value">{self._escape_html(evalue)}</span>
            </div>
            <div class="error-traceback">
                {traceback_html}
            </div>
        </div>
        '''
    
    def set_jupyter_data(self, outputs: List[Dict], execution_count: int = None, metadata: Dict = None):
        """Set Jupyter cell data for display"""
        self.jupyter_outputs = outputs
        self.execution_count = execution_count
        if metadata:
            self.jupyter_metadata = metadata