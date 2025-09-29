"""
Jupyter Code Cell Widget Implementation
Extends python code widget to handle Jupyter notebook code cells with outputs
"""

import sys
import os
import json
import base64
from typing import Dict, Any, Optional, List

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'python-code'))

from base_widget import WidgetExecutor
from python_code import PythonCodeWidget


class JupyterCodeCellWidget(PythonCodeWidget):
    """
    Jupyter code cell widget that extends python code functionality
    with support for cell outputs, execution counts, and metadata
    """
    
    # Override input/output variable declarations
    input_variables = {
        'code': '# Jupyter code cell\nprint("Hello from Jupyter!")',
        'execute_immediately': False,
        'cell_metadata': {},
        'outputs': [],
        'execution_count': None,
        'cell_index': 0
    }
    
    output_variables = {
        'success': True,
        'stdout': '',
        'stderr': '',
        'return_value': None,
        'execution_time': 0.0,
        'cell_type': 'code',
        'rendered_outputs': [],
        'execution_count': None
    }
    
    def _execute_impl(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Jupyter code cell widget"""
        code = validated_input.get('code', '')
        execute_immediately = validated_input.get('execute_immediately', False)
        cell_metadata = validated_input.get('cell_metadata', {})
        outputs = validated_input.get('outputs', [])
        execution_count = validated_input.get('execution_count')
        cell_index = validated_input.get('cell_index', 0)
        
        # If not executing immediately, just render the existing outputs
        if not execute_immediately and outputs:
            rendered_outputs = self.render_jupyter_outputs(outputs)
            
            return {
                'success': True,
                'stdout': '',
                'stderr': '',
                'return_value': None,
                'execution_time': 0.0,
                'cell_type': 'code',
                'rendered_outputs': rendered_outputs,
                'execution_count': execution_count,
                'metadata': {
                    'cell_type': 'code',
                    'cell_index': cell_index,
                    'code_length': len(code),
                    'has_outputs': len(outputs) > 0,
                    'cell_metadata': cell_metadata
                }
            }
        
        # Execute the code using parent class functionality
        base_result = super()._execute_impl({
            'code': code,
            'execute_immediately': execute_immediately
        })
        
        # Enhance result with Jupyter-specific information
        base_result.update({
            'cell_type': 'code',
            'rendered_outputs': self.render_jupyter_outputs(outputs) if outputs else [],
            'execution_count': execution_count,
            'metadata': {
                'cell_type': 'code',
                'cell_index': cell_index,
                'code_length': len(code),
                'has_outputs': len(outputs) > 0,
                'cell_metadata': cell_metadata
            }
        })
        
        return base_result
    
    def render_jupyter_outputs(self, outputs: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Render Jupyter notebook outputs to HTML"""
        rendered = []
        
        for output in outputs:
            output_type = output.get('output_type', '')
            
            if output_type == 'stream':
                # Handle stream output (stdout, stderr)
                stream_name = output.get('name', 'stdout')
                text = output.get('text', [])
                if isinstance(text, list):
                    text = ''.join(text)
                
                rendered.append({
                    'type': 'stream',
                    'stream_name': stream_name,
                    'html': f'<pre class="jupyter-stream jupyter-{stream_name}">{self.escape_html(text)}</pre>'
                })
            
            elif output_type == 'display_data' or output_type == 'execute_result':
                # Handle display data and execution results
                data = output.get('data', {})
                metadata = output.get('metadata', {})
                
                for mime_type, content in data.items():
                    if mime_type == 'text/html':
                        # HTML content
                        if isinstance(content, list):
                            content = ''.join(content)
                        rendered.append({
                            'type': 'html',
                            'mime_type': mime_type,
                            'html': f'<div class="jupyter-html-output">{content}</div>'
                        })
                    
                    elif mime_type == 'text/plain':
                        # Plain text output
                        if isinstance(content, list):
                            content = ''.join(content)
                        rendered.append({
                            'type': 'text',
                            'mime_type': mime_type,
                            'html': f'<pre class="jupyter-text-output">{self.escape_html(content)}</pre>'
                        })
                    
                    elif mime_type.startswith('image/'):
                        # Image output
                        if isinstance(content, list):
                            content = ''.join(content)
                        data_url = f"data:{mime_type};base64,{content}"
                        rendered.append({
                            'type': 'image',
                            'mime_type': mime_type,
                            'html': f'<img src="{data_url}" class="jupyter-image-output" alt="Output image" />'
                        })
                    
                    elif mime_type == 'application/json':
                        # JSON output
                        json_str = json.dumps(content, indent=2) if not isinstance(content, str) else content
                        rendered.append({
                            'type': 'json',
                            'mime_type': mime_type,
                            'html': f'<pre class="jupyter-json-output">{self.escape_html(json_str)}</pre>'
                        })
            
            elif output_type == 'error':
                # Handle error output
                ename = output.get('ename', 'Error')
                evalue = output.get('evalue', '')
                traceback = output.get('traceback', [])
                
                if isinstance(traceback, list):
                    traceback_text = '\n'.join(traceback)
                else:
                    traceback_text = str(traceback)
                
                rendered.append({
                    'type': 'error',
                    'html': f'''
                    <div class="jupyter-error-output">
                        <div class="error-name">{self.escape_html(ename)}</div>
                        <div class="error-value">{self.escape_html(evalue)}</div>
                        <pre class="error-traceback">{self.escape_html(traceback_text)}</pre>
                    </div>
                    '''
                })
        
        return rendered
    
    def escape_html(self, text: str) -> str:
        """Escape HTML characters"""
        import html
        return html.escape(text)
    
    def render_cell_html(self, code: str, outputs: List[Dict[str, str]], execution_count: Optional[int], cell_index: int) -> str:
        """Render complete cell as HTML with code and outputs"""
        execution_label = f"[{execution_count}]" if execution_count is not None else "[ ]"
        
        outputs_html = ""
        if outputs:
            outputs_html = '<div class="cell-outputs">' + ''.join([output['html'] for output in outputs]) + '</div>'
        
        return f'''
        <div class="jupyter-code-cell" data-cell-index="{cell_index}">
            <div class="cell-header">
                <span class="cell-type-badge">Code</span>
                <span class="cell-index">Cell {cell_index}</span>
                <span class="execution-count">{execution_label}</span>
            </div>
            <div class="cell-input">
                <pre class="code-content"><code>{self.escape_html(code)}</code></pre>
            </div>
            {outputs_html}
        </div>
        '''
    
    # Action methods for Jupyter-specific operations
    def action_export_cell(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Action to export cell back to Jupyter format"""
        result = self._execute_impl(validated_input)
        
        if result['success']:
            jupyter_cell = {
                'cell_type': 'code',
                'metadata': validated_input.get('cell_metadata', {}),
                'source': validated_input.get('code', '').split('\n'),
                'execution_count': validated_input.get('execution_count'),
                'outputs': validated_input.get('outputs', [])
            }
            
            result['action'] = 'export-cell'
            result['jupyter_cell'] = jupyter_cell
        
        return result
    
    def action_execute_cell(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Action to execute the cell code"""
        # Force execution
        validated_input['execute_immediately'] = True
        return self._execute_impl(validated_input)


# Widget schema definition for Jupyter code cell
JUPYTER_CODE_CELL_SCHEMA = {
    "id": "jupyter-code-cell",
    "name": "Jupyter Code Cell",
    "description": "Code cell from Jupyter notebook with output display support",
    "category": "computation",
    "icon": "🐍",
    "input_schema": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Python code from notebook cell",
                "default": "# Jupyter code cell\nprint(\"Hello from Jupyter!\")"
            },
            "execute_immediately": {
                "type": "boolean",
                "description": "Execute code immediately",
                "default": False
            },
            "cell_metadata": {
                "type": "object",
                "description": "Original Jupyter cell metadata",
                "default": {}
            },
            "outputs": {
                "type": "array",
                "description": "Jupyter cell outputs",
                "default": []
            },
            "execution_count": {
                "type": ["integer", "null"],
                "description": "Execution count from notebook"
            },
            "cell_index": {
                "type": "integer",
                "description": "Index of cell in original notebook",
                "default": 0
            }
        },
        "required": ["code"]
    },
    "output_schema": {
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "stdout": {"type": "string"},
            "stderr": {"type": "string"},
            "return_value": {},
            "execution_time": {"type": "number"},
            "cell_type": {"type": "string", "enum": ["code"]},
            "rendered_outputs": {"type": "array"},
            "execution_count": {"type": ["integer", "null"]}
        },
        "required": ["success"]
    },
    "actions": {
        "execute-cell": {
            "slug": "execute-cell",
            "name": "Execute Cell",
            "description": "Execute the code cell",
            "output_format": "json"
        },
        "export-cell": {
            "slug": "export-cell",
            "name": "Export Cell",
            "description": "Export cell back to Jupyter format",
            "output_format": "json"
        }
    }
}


def create_jupyter_code_cell_widget(widget_schema: Dict[str, Any], jsonld_schema: Dict[str, Any] = None) -> JupyterCodeCellWidget:
    """Factory function to create Jupyter code cell widget instance"""
    return JupyterCodeCellWidget(widget_schema, jsonld_schema)