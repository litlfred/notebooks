"""
Widget Execution Engine
Handles JSON schema-based widget execution with Python scripts
"""

import json
import re
import time
from typing import Dict, Any, List, Optional

class WidgetExecutor:
    """Base class for executing schema-based widgets"""
    
    def __init__(self, widget_schema: Dict[str, Any]):
        self.schema = widget_schema
        self.id = widget_schema['id']
        self.name = widget_schema['name']
        self.input_schema = widget_schema['input_schema']
        self.output_schema = widget_schema['output_schema']
        
    def validate_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input data against schema"""
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
        validated_input = self.validate_input(input_data)
        
        # Record execution time
        start_time = time.time()
        
        try:
            result = self._execute_impl(validated_input)
            result['execution_time'] = (time.time() - start_time) * 1000
            result['widget_id'] = self.id
            result['success'] = True
            return result
            
        except Exception as e:
            return {
                'widget_id': self.id,
                'success': False,
                'error': str(e),
                'execution_time': (time.time() - start_time) * 1000
            }
    
    def _execute_impl(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Override this method in subclasses"""
        raise NotImplementedError

class MarkdownWidget(WidgetExecutor):
    """Markdown widget with LaTeX and variable substitution"""
    
    def _execute_impl(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        content = validated_input['content']
        variables = validated_input.get('variables', {})
        render_latex = validated_input.get('render_latex', True)
        
        # Find variables in content
        variables_used = self._find_variables(content)
        
        # Substitute variables
        substituted_content = self._substitute_variables(content, variables)
        
        # Render markdown to HTML
        rendered_html = self._render_markdown(substituted_content, render_latex)
        
        return {
            'rendered_html': rendered_html,
            'variables_used': variables_used,
            'substituted_content': substituted_content
        }
    
    def _find_variables(self, content: str) -> List[str]:
        """Find variable references in content like {{variable_name}}"""
        pattern = r'\{\{([a-zA-Z_][a-zA-Z0-9_]*)\}\}'
        matches = re.findall(pattern, content)
        return list(set(matches))
    
    def _substitute_variables(self, content: str, variables: Dict[str, Any]) -> str:
        """Replace {{variable}} with actual values"""
        def replace_var(match):
            var_name = match.group(1)
            if var_name in variables:
                return str(variables[var_name])
            else:
                return f"{{undefined:{var_name}}}"
        
        pattern = r'\{\{([a-zA-Z_][a-zA-Z0-9_]*)\}\}'
        return re.sub(pattern, replace_var, content)
    
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
        html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
        
        # LaTeX math (preserve for MathJax)
        if render_latex:
            # Keep LaTeX expressions as-is for client-side rendering
            pass
        
        # Line breaks
        html = html.replace('\n', '<br>')
        
        return html

class PythonWidget(WidgetExecutor):
    """Python code execution widget"""
    
    def _execute_impl(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        code = validated_input['code']
        imports = validated_input.get('imports', [])
        input_variables = validated_input.get('variables', {})
        
        # Prepare execution environment
        exec_globals = {
            '__builtins__': __builtins__,
            'print': self._capture_print,
            'result': None
        }
        
        # Add input variables
        exec_globals.update(input_variables)
        
        # Add imports
        for imp in imports:
            try:
                if ' as ' in imp:
                    module_name, alias = imp.split(' as ')
                    exec_globals[alias.strip()] = __import__(module_name.strip())
                else:
                    exec_globals[imp] = __import__(imp)
            except ImportError:
                pass  # Skip unavailable imports
        
        # Capture stdout
        self.stdout_capture = []
        self.stderr_capture = []
        
        try:
            # Execute code
            exec(code, exec_globals)
            
            # Extract result and variables
            result = exec_globals.get('result')
            variables = {k: v for k, v in exec_globals.items() 
                        if not k.startswith('__') and k not in ['print', 'result']}
            
            return {
                'result': result,
                'stdout': '\n'.join(self.stdout_capture),
                'stderr': '\n'.join(self.stderr_capture),
                'variables': self._serialize_variables(variables)
            }
            
        except Exception as e:
            self.stderr_capture.append(str(e))
            return {
                'result': None,
                'stdout': '\n'.join(self.stdout_capture),
                'stderr': '\n'.join(self.stderr_capture),
                'variables': {}
            }
    
    def _capture_print(self, *args, **kwargs):
        """Capture print statements"""
        output = ' '.join(str(arg) for arg in args)
        self.stdout_capture.append(output)
    
    def _serialize_variables(self, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Convert variables to JSON-serializable format"""
        serialized = {}
        for name, value in variables.items():
            try:
                # Try to serialize
                json.dumps(value)
                serialized[name] = value
            except (TypeError, ValueError):
                # Can't serialize, store type info
                serialized[name] = f"<{type(value).__name__}>"
        return serialized

class DataGeneratorWidget(WidgetExecutor):
    """Generate synthetic datasets"""
    
    def _execute_impl(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        import numpy as np
        
        data_type = validated_input['type']
        n_points = validated_input['n_points']
        parameters = validated_input.get('parameters', {})
        x_range = validated_input.get('x_range', {'min': 0, 'max': 10})
        
        # Generate x values
        x = np.linspace(x_range['min'], x_range['max'], n_points)
        
        # Generate y values based on type
        amplitude = parameters.get('amplitude', 1.0)
        frequency = parameters.get('frequency', 1.0)
        phase = parameters.get('phase', 0.0)
        noise = parameters.get('noise', 0.1)
        
        if data_type == 'sine':
            y = amplitude * np.sin(frequency * x + phase)
        elif data_type == 'cosine':
            y = amplitude * np.cos(frequency * x + phase)
        elif data_type == 'linear':
            slope = parameters.get('slope', 1.0)
            y = amplitude * slope * x + phase
        elif data_type == 'polynomial':
            coeffs = parameters.get('coefficients', [1, 0, 0])  # x^2
            y = np.polyval(coeffs, x) * amplitude
        elif data_type == 'random':
            y = amplitude * np.random.random(n_points)
        elif data_type == 'normal':
            y = amplitude * np.random.normal(0, 1, n_points)
        else:
            y = np.zeros(n_points)
        
        # Add noise
        if noise > 0:
            y += np.random.normal(0, noise * amplitude, n_points)
        
        return {
            'data': {
                'x': x.tolist(),
                'y': y.tolist()
            },
            'metadata': {
                'generator_type': data_type,
                'parameters_used': parameters,
                'generated_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        }

# Widget factory
def create_widget(widget_id: str, schemas: Dict[str, Any]) -> WidgetExecutor:
    """Factory function to create widgets"""
    schema = schemas['widget-schemas'][widget_id]
    
    if widget_id == 'markdown-note':
        return MarkdownWidget(schema)
    elif widget_id == 'python-code':
        return PythonWidget(schema)
    elif widget_id == 'data-generator':
        return DataGeneratorWidget(schema)
    else:
        return WidgetExecutor(schema)  # Basic implementation

# Widget connection system
class WidgetGraph:
    """Manages widget connections and execution order"""
    
    def __init__(self):
        self.widgets = {}
        self.connections = {}
        self.schemas = {}
    
    def add_widget(self, widget_id: str, widget_type: str, config: Dict[str, Any]):
        """Add a widget instance to the graph"""
        widget = create_widget(widget_type, self.schemas)
        self.widgets[widget_id] = {
            'executor': widget,
            'config': config,
            'type': widget_type
        }
    
    def connect_widgets(self, source_id: str, target_id: str, 
                       output_path: str, input_path: str):
        """Connect output from one widget to input of another"""
        if source_id not in self.connections:
            self.connections[source_id] = []
        
        self.connections[source_id].append({
            'target': target_id,
            'output_path': output_path,
            'input_path': input_path
        })
    
    def execute_widget(self, widget_id: str, force_recompute: bool = False) -> Dict[str, Any]:
        """Execute a widget with dependency resolution"""
        if widget_id not in self.widgets:
            raise ValueError(f"Widget {widget_id} not found")
        
        widget_info = self.widgets[widget_id]
        executor = widget_info['executor']
        config = widget_info['config'].copy()
        
        # Resolve input dependencies
        for source_id, connections in self.connections.items():
            for conn in connections:
                if conn['target'] == widget_id:
                    # Execute source widget if needed
                    source_result = self.execute_widget(source_id, force_recompute)
                    
                    # Extract output value
                    output_value = self._get_nested_value(
                        source_result, conn['output_path']
                    )
                    
                    # Set input value
                    self._set_nested_value(
                        config, conn['input_path'], output_value
                    )
        
        # Execute widget
        return executor.execute(config)
    
    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """Get value from nested dict using dot notation"""
        keys = path.split('.')
        current = data
        for key in keys:
            current = current[key]
        return current
    
    def _set_nested_value(self, data: Dict[str, Any], path: str, value: Any):
        """Set value in nested dict using dot notation"""
        keys = path.split('.')
        current = data
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value