"""
Jupyter Markdown Cell Widget Implementation
Extends sticky note widget to handle Jupyter notebook markdown cells with attachments
"""

import sys
import os
import json
import base64
from typing import Dict, Any, Optional

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'sticky-note'))

from base_widget import WidgetExecutor
from sticky_note import StickyNoteWidget


class JupyterMarkdownCellWidget(StickyNoteWidget):
    """
    Jupyter markdown cell widget that extends sticky note functionality
    with support for cell attachments and metadata
    """
    
    # Override input/output variable declarations
    input_variables = {
        'content': '# Jupyter Markdown Cell\n\nMarkdown content from notebook cell...',
        'show_note': True,
        'cell_metadata': {},
        'attachments': {},
        'execution_count': None,
        'cell_index': 0
    }
    
    output_variables = {
        'success': True,
        'rendered_html': '',
        'metadata': {},
        'cell_type': 'markdown',
        'processed_attachments': {}
    }
    
    def _execute_impl(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Jupyter markdown cell widget"""
        content = validated_input.get('content', '')
        show_note = validated_input.get('show_note', True)
        cell_metadata = validated_input.get('cell_metadata', {})
        attachments = validated_input.get('attachments', {})
        cell_index = validated_input.get('cell_index', 0)
        
        if not show_note:
            return {
                'success': True,
                'rendered_html': '<div class="jupyter-markdown-cell hidden">Markdown cell hidden</div>',
                'metadata': {
                    'visible': False,
                    'cell_type': 'markdown',
                    'cell_index': cell_index,
                    'content_length': len(content)
                },
                'cell_type': 'markdown',
                'processed_attachments': {}
            }
        
        # Process attachments first
        processed_attachments = self.process_attachments(attachments)
        
        # Process content with attachment references
        processed_content = self.process_attachment_references(content, processed_attachments)
        
        # Render markdown with attachment support
        html_content = self.render_simple_markdown(processed_content)
        
        # Add cell styling
        styled_html = f'''
        <div class="jupyter-markdown-cell" data-cell-index="{cell_index}">
            <div class="cell-header">
                <span class="cell-type-badge">Markdown</span>
                <span class="cell-index">Cell {cell_index}</span>
            </div>
            <div class="cell-content">
                {html_content}
            </div>
        </div>
        '''
        
        return {
            'success': True,
            'rendered_html': styled_html,
            'metadata': {
                'visible': True,
                'cell_type': 'markdown',
                'cell_index': cell_index,
                'content_length': len(content),
                'rendered_length': len(html_content),
                'has_attachments': len(attachments) > 0,
                'cell_metadata': cell_metadata
            },
            'cell_type': 'markdown',
            'processed_attachments': processed_attachments
        }
    
    def process_attachments(self, attachments: Dict[str, Any]) -> Dict[str, str]:
        """Process notebook cell attachments into data URLs"""
        processed = {}
        
        for attachment_name, attachment_data in attachments.items():
            if isinstance(attachment_data, dict):
                # Handle different MIME types
                for mime_type, data in attachment_data.items():
                    if mime_type.startswith('image/'):
                        # Convert base64 image data to data URL
                        if isinstance(data, list):
                            data = ''.join(data)
                        data_url = f"data:{mime_type};base64,{data}"
                        processed[attachment_name] = data_url
                        break
                    elif mime_type == 'text/plain':
                        # Handle text attachments
                        if isinstance(data, list):
                            data = ''.join(data)
                        processed[attachment_name] = data
        
        return processed
    
    def process_attachment_references(self, content: str, attachments: Dict[str, str]) -> str:
        """Replace attachment references in markdown content"""
        import re
        
        # Replace attachment:filename references with data URLs
        def replace_attachment(match):
            filename = match.group(1)
            if filename in attachments:
                return attachments[filename]
            return match.group(0)  # Return original if not found
        
        # Pattern for attachment references: ![alt](attachment:filename)
        content = re.sub(r'!\[([^\]]*)\]\(attachment:([^)]+)\)', 
                        lambda m: f'![{m.group(1)}]({attachments.get(m.group(2), m.group(0))})', 
                        content)
        
        return content
    
    # Action methods for Jupyter-specific operations
    def action_export_cell(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Action to export cell back to Jupyter format"""
        result = self._execute_impl(validated_input)
        
        if result['success']:
            jupyter_cell = {
                'cell_type': 'markdown',
                'metadata': validated_input.get('cell_metadata', {}),
                'source': validated_input.get('content', '').split('\n'),
                'attachments': validated_input.get('attachments', {})
            }
            
            result['action'] = 'export-cell'
            result['jupyter_cell'] = jupyter_cell
        
        return result


# Widget schema definition for Jupyter markdown cell
JUPYTER_MARKDOWN_CELL_SCHEMA = {
    "id": "jupyter-markdown-cell",
    "name": "Jupyter Markdown Cell",
    "description": "Markdown cell from Jupyter notebook with attachment support",
    "category": "content",
    "icon": "📝",
    "input_schema": {
        "type": "object",
        "properties": {
            "content": {
                "type": "string",
                "description": "Markdown content from notebook cell",
                "default": "# Jupyter Markdown Cell\n\nMarkdown content from notebook cell..."
            },
            "show_note": {
                "type": "boolean",
                "description": "Show or hide the cell content",
                "default": True
            },
            "cell_metadata": {
                "type": "object",
                "description": "Original Jupyter cell metadata",
                "default": {}
            },
            "attachments": {
                "type": "object",
                "description": "Cell attachments (images, files)",
                "default": {}
            },
            "execution_count": {
                "type": ["integer", "null"],
                "description": "Execution count (null for markdown cells)"
            },
            "cell_index": {
                "type": "integer",
                "description": "Index of cell in original notebook",
                "default": 0
            }
        },
        "required": ["content"]
    },
    "output_schema": {
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "rendered_html": {"type": "string"},
            "metadata": {"type": "object"},
            "cell_type": {"type": "string", "enum": ["markdown"]},
            "processed_attachments": {"type": "object"}
        },
        "required": ["success"]
    },
    "actions": {
        "render-markdown": {
            "slug": "render-markdown",
            "name": "Render Markdown",
            "description": "Render markdown content with attachment support",
            "output_format": "html"
        },
        "export-cell": {
            "slug": "export-cell",
            "name": "Export Cell",
            "description": "Export cell back to Jupyter format",
            "output_format": "json"
        }
    }
}


def create_jupyter_markdown_cell_widget(widget_schema: Dict[str, Any], jsonld_schema: Dict[str, Any] = None) -> JupyterMarkdownCellWidget:
    """Factory function to create Jupyter markdown cell widget instance"""
    return JupyterMarkdownCellWidget(widget_schema, jsonld_schema)