"""
Jupyter Markdown Cell Widget Executor
Handles markdown cells imported from Jupyter notebooks with enhanced rendering
"""

from .sticky_note import MarkdownWidget
import re


class JupyterMarkdownWidget(MarkdownWidget):
    """Jupyter markdown cell widget - extends sticky note functionality"""
    
    def _execute_impl(self, validated_input):
        """Execute markdown rendering with Jupyter-specific enhancements"""
        
        # Call parent implementation
        result = super()._execute_impl(validated_input)
        
        # Add Jupyter-specific metadata to output
        if hasattr(self, 'jupyter_metadata'):
            result['jupyter_metadata'] = self.jupyter_metadata
        
        # Handle Jupyter-specific markdown features
        content = validated_input['content']
        
        # Process Jupyter markdown extensions
        enhanced_content = self._process_jupyter_markdown(content)
        
        # Re-render with enhanced content if changes were made
        if enhanced_content != content:
            enhanced_result = super()._execute_impl({
                **validated_input,
                'content': enhanced_content
            })
            result['rendered_html'] = enhanced_result['rendered_html']
        
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