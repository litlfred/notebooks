"""
Sticky Note Widget Implementation
Simple markdown widget that serves as the most basic widget example.
"""

import re
from typing import Dict, Any
from base_widget import WidgetExecutor


class StickyNoteWidget(WidgetExecutor):
    """
    Simplest widget implementation - functions as a markdown sticky note.
    
    Input: markdown content with show/hide toggle
    Output: rendered HTML 
    """
    
    # Override input/output variable declarations
    input_variables = {
        'content': '# New Sticky Note\n\nClick edit to add your **markdown** content...',
        'show_note': True
    }
    
    output_variables = {
        'success': True,
        'rendered_html': '',
        'metadata': {}
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
        Enhanced markdown rendering with variable substitution and LaTeX support.
        Supports: headers, bold, italic, code blocks, lists, variables, math symbols
        """
        html = content
        
        # Process variable substitution first
        html = self.process_markdown_variables(html)
        
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
        
        # Mathematical symbols (LaTeX-like)
        html = html.replace('\\wp', '℘')
        html = html.replace('\\Z', 'ℤ')
        html = html.replace('\\C', 'ℂ')
        html = html.replace('\\R', 'ℝ')
        html = html.replace('\\L', 'L')
        html = html.replace('\\T', 'T')
        
        # Convert line breaks to HTML
        html = html.replace('\n\n', '</p><p>').replace('\n', '<br>')
        html = f'<p>{html}</p>'
        
        # Clean up empty paragraphs
        html = re.sub(r'<p>\s*</p>', '', html)
        
        return html
    
    def process_markdown_variables(self, content: str) -> str:
        """
        Process variable substitution in markdown content.
        Supports {{variable_name}} syntax with widget metadata.
        """
        # Get widget metadata variables
        variables = {
            'widget_id': self.id,
            'widget_name': self.name,
            'timestamp': self._get_current_timestamp()
        }
        
        # Add any additional variables from widget configuration  
        if hasattr(self, 'variables') and isinstance(self.variables, dict):
            variables.update(self.variables)
        
        # Process variable substitution
        variable_pattern = re.compile(r'\{\{([a-zA-Z_][a-zA-Z0-9_]*)\}\}')
        
        def replace_variable(match):
            var_name = match.group(1)
            if var_name in variables:
                return str(variables[var_name])
            else:
                # Return error marker for undefined variables
                return f'<span style="color: red; text-decoration: underline;">{{undefined:{var_name}}}</span>'
        
        return variable_pattern.sub(replace_variable, content)
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    # Action methods for multi-action support as defined in the schema
    def action_render_markdown(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Render markdown content action"""
        result = self._execute_impl(validated_input)
        result['action_type'] = 'render-markdown'
        result['output_format'] = 'html'
        return result
    
    def action_export_pdf(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Export note as PDF action (mock implementation)"""
        content = validated_input.get('content', '')
        
        return {
            'success': True,
            'action_type': 'export-pdf',
            'output_format': 'pdf',
            'message': 'PDF export functionality would be implemented here',
            'content_length': len(content),
            'export_ready': True
        }
    
    def action_export_html(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Export note as HTML file action"""
        result = self._execute_impl(validated_input)
        html_content = result.get('rendered_html', '')
        
        return {
            'success': True,
            'action_type': 'export-html',
            'output_format': 'html',
            'html_content': html_content,
            'standalone_html': f'<!DOCTYPE html><html><head><title>Sticky Note</title></head><body>{html_content}</body></html>',
            'message': 'HTML export ready'
        }


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
    "actions": {
        "render-markdown": {
            "slug": "render-markdown",
            "names": {
                "en": "Render Markdown",
                "es": "Renderizar Markdown",
                "fr": "Rendre Markdown",
                "de": "Markdown Rendern"
            },
            "icon": "📝",
            "description": {
                "en": "Render markdown content with LaTeX support",
                "es": "Renderizar contenido markdown con soporte LaTeX"
            },
            "menu_category": "display",
            "output_format": "html",
            "validation_required": True
        },
        "export-pdf": {
            "slug": "export-pdf",
            "names": {
                "en": "Export PDF",
                "es": "Exportar PDF", 
                "fr": "Exporter PDF",
                "de": "PDF Exportieren"
            },
            "icon": "📄",
            "description": {
                "en": "Export note as PDF document"
            },
            "menu_category": "export",
            "output_format": "pdf",
            "validation_required": True
        },
        "export-html": {
            "slug": "export-html",
            "names": {
                "en": "Export HTML",
                "es": "Exportar HTML",
                "fr": "Exporter HTML", 
                "de": "HTML Exportieren"
            },
            "icon": "🌐",
            "description": {
                "en": "Export note as standalone HTML file"
            },
            "menu_category": "export",
            "output_format": "html",
            "validation_required": True
        }
    },
    "python_script": "libraries/core/sticky-note/sticky_note.py"
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