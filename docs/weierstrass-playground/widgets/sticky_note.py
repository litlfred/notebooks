"""
Sticky Note Widget Implementation
Simple markdown widget that serves as the most basic widget example.
"""

import re
from typing import Dict, Any


class StickyNoteWidget:
    """
    Simplest widget implementation - functions as a markdown sticky note.
    
    Input: markdown content with show/hide toggle
    Output: rendered HTML 
    """
    
    def __init__(self, widget_schema: Dict[str, Any]):
        self.schema = widget_schema
        self.id = widget_schema['id']
        self.name = widget_schema['name']
        self.input_schema = widget_schema['input_schema']
        self.output_schema = widget_schema['output_schema']
    
    def validate_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input data against schema and apply defaults"""
        validated = {}
        
        # Apply defaults for missing values
        if 'properties' in self.input_schema:
            for prop, prop_schema in self.input_schema['properties'].items():
                if prop in input_data:
                    validated[prop] = input_data[prop]
                elif 'default' in prop_schema:
                    validated[prop] = prop_schema['default']
                elif prop in self.input_schema.get('required', []):
                    raise ValueError(f"Required property '{prop}' missing")
        
        return validated
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute widget with validated input"""
        try:
            validated_input = self.validate_input(input_data)
            return self._execute_impl(validated_input)
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'rendered_html': f'<div class="error">Error: {str(e)}</div>'
            }
    
    def _execute_impl(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the sticky note widget"""
        content = validated_input.get('content', '')
        show_note = validated_input.get('show_note', True)
        
        if not show_note:
            return {
                'success': True,
                'rendered_html': '<div class="sticky-note hidden">Note hidden</div>',
                'metadata': {
                    'visible': False,
                    'content_length': len(content)
                }
            }
        
        # Simple markdown-like rendering
        html_content = self.render_simple_markdown(content)
        
        return {
            'success': True,
            'rendered_html': f'<div class="sticky-note">{html_content}</div>',
            'metadata': {
                'visible': True,
                'content_length': len(content),
                'rendered_length': len(html_content)
            }
        }
    
    def render_simple_markdown(self, content: str) -> str:
        """
        Simple markdown rendering for basic formatting.
        Supports: headers, bold, italic, code blocks, lists
        """
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
        
        # Simple lists
        lines = html.split('\n')
        processed_lines = []
        in_list = False
        
        for line in lines:
            if re.match(r'^\s*[-*+]\s+', line):
                if not in_list:
                    processed_lines.append('<ul>')
                    in_list = True
                list_item = re.sub(r'^\s*[-*+]\s+', '', line)
                processed_lines.append(f'<li>{list_item}</li>')
            else:
                if in_list:
                    processed_lines.append('</ul>')
                    in_list = False
                processed_lines.append(line)
        
        if in_list:
            processed_lines.append('</ul>')
        
        html = '\n'.join(processed_lines)
        
        # Convert line breaks to HTML
        html = html.replace('\n\n', '</p><p>').replace('\n', '<br>')
        html = f'<p>{html}</p>'
        
        # Clean up empty paragraphs
        html = re.sub(r'<p>\s*</p>', '', html)
        
        return html


# Widget schema definition for the sticky note
STICKY_NOTE_SCHEMA = {
    "id": "sticky-note",
    "name": "Sticky Note", 
    "description": "Simple markdown note widget - the most basic widget example",
    "category": "content",
    "icon": "📝",
    "input_schema": {
        "type": "object",
        "properties": {
            "content": {
                "type": "string",
                "description": "Markdown content for the note",
                "default": "# New Sticky Note\n\nClick edit to add your **markdown** content...\n\n- Use lists\n- Add `code`\n- Format *text*"
            },
            "show_note": {
                "type": "boolean",
                "description": "Show or hide the note content", 
                "default": True
            }
        },
        "required": ["content"]
    },
    "output_schema": {
        "type": "object",
        "properties": {
            "success": {
                "type": "boolean",
                "description": "Whether execution succeeded"
            },
            "rendered_html": {
                "type": "string",
                "description": "Rendered HTML output"
            },
            "error": {
                "type": "string",
                "description": "Error message if execution failed"
            },
            "metadata": {
                "type": "object",
                "properties": {
                    "visible": {"type": "boolean"},
                    "content_length": {"type": "integer"},
                    "rendered_length": {"type": "integer"}
                },
                "description": "Execution metadata"
            }
        }
    },
    "python_script": "widgets/sticky_note.py"
}


def create_sticky_note_widget():
    """Factory function to create sticky note widget instance"""
    return StickyNoteWidget(STICKY_NOTE_SCHEMA)


if __name__ == "__main__":
    # Test the sticky note widget
    widget = create_sticky_note_widget()
    
    # Test with default content
    result = widget.execute({})
    print("Default execution:")
    print(result)
    print()
    
    # Test with custom content  
    result = widget.execute({
        "content": "# Test Note\n\nThis is a **test** with *formatting*.\n\n- Item 1\n- Item 2\n\n`code example`",
        "show_note": True
    })
    print("Custom content execution:")
    print(result)
    print()
    
    # Test with hidden note
    result = widget.execute({
        "content": "Hidden content",
        "show_note": False
    })
    print("Hidden note execution:")
    print(result)