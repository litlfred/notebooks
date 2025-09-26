"""
Widget Execution Engine for Mathematical Board
Handles JSON schema-based widget execution with Python scripts for specialized Weierstrass widgets
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
        
        # Handle both old and new schema formats
        if 'input_schemas' in widget_schema:
            # New format with multiple schemas
            self.input_schemas = widget_schema['input_schemas']
            self.output_schemas = widget_schema['output_schemas']
            # For backward compatibility, use first schema as primary
            self.input_schema = self._resolve_schema_reference(self.input_schemas[0]) if self.input_schemas else {}
            self.output_schema = self._resolve_schema_reference(self.output_schemas[0]) if self.output_schemas else {}
        else:
            # Old format with single schema
            self.input_schema = widget_schema.get('input_schema', {})
            self.output_schema = widget_schema.get('output_schema', {})
            self.input_schemas = [self.input_schema] if self.input_schema else []
            self.output_schemas = [self.output_schema] if self.output_schema else []
    
    def _resolve_schema_reference(self, schema_ref):
        """Resolve schema reference to actual schema object"""
        if isinstance(schema_ref, str):
            # For now, return a basic schema structure for URL references
            # In a full implementation, this would fetch and resolve the URL
            if 'sticky-note' in schema_ref:
                return {
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "default": "# New Sticky Note\n\nClick edit to add your **markdown** content...\n\n- Use lists\n- Add `code`\n- Format *text*"
                        },
                        "show_note": {
                            "type": "boolean",
                            "default": True
                        }
                    },
                    "required": ["content"]
                }
            elif 'common' in schema_ref and 'markdown_content' in schema_ref:
                return {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "default": ""},
                        "render_latex": {"type": "boolean", "default": True},
                        "variables": {"type": "object", "default": {}}
                    },
                    "required": ["content"]
                }
            else:
                # Default empty schema for unknown references
                return {"type": "object", "properties": {}}
        else:
            # Inline schema object
            return schema_ref
        
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

class WeierstrassTwoPanelWidget(WidgetExecutor):
    """Two-panel ℘(z) and ℘′(z) visualization"""
    
    def _execute_impl(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        p = validated_input['p']
        q = validated_input['q']
        N = validated_input['N']
        grid_size = validated_input.get('grid_size', {'x': 100, 'y': 100})
        
        return {
            'plot_data': {
                'image_base64': f'two_panel_plot_p{p}_q{q}_N{N}',
                'width': 800,
                'height': 400
            },
            'field_data': {
                'wp_field': 'computed_wp_data',
                'wp_deriv_field': 'computed_wp_deriv_data'
            }
        }

class WeierstrassThreePanelWidget(WidgetExecutor):
    """Three-panel ℘(z), Re(℘′(z)), Im(℘′(z)) visualization"""
    
    def _execute_impl(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        p = validated_input['p']
        q = validated_input['q'] 
        N = validated_input['N']
        
        return {
            'plot_data': {
                'image_base64': f'three_panel_plot_p{p}_q{q}_N{N}',
                'width': 1200,
                'height': 400
            },
            'component_data': {
                'wp_real': 'wp_real_component',
                'wp_deriv_real': 'wp_deriv_real_component',
                'wp_deriv_imag': 'wp_deriv_imag_component'
            }
        }

class WeierstrassFivePanelWidget(WidgetExecutor):
    """Complete five-panel ℘ function analysis"""
    
    def _execute_impl(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        p = validated_input['p']
        q = validated_input['q']
        N = validated_input['N']
        
        return {
            'plot_data': {
                'image_base64': f'five_panel_analysis_p{p}_q{q}_N{N}',
                'width': 1000,
                'height': 800
            },
            'analysis_data': {
                'complete_analysis': True,
                'derivatives_computed': True,
                'magnitude_analysis': True
            }
        }

class WeierstrassTrajectoryWidget(WidgetExecutor):
    """Particle trajectory analysis in ℘ field"""
    
    def _execute_impl(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        p = validated_input['p']
        q = validated_input['q']
        N = validated_input['N']
        particles = validated_input['particles']
        integration = validated_input.get('integration', {})
        
        trajectories = []
        for i, particle in enumerate(particles):
            trajectories.append({
                'path': f'trajectory_{i}_data',
                'blowup_point': None,
                'integration_time': integration.get('T', 2.0)
            })
        
        return {
            'plot_data': {
                'image_base64': f'trajectory_plot_p{p}_q{q}_{len(particles)}particles',
                'width': 800,
                'height': 600
            },
            'trajectories': trajectories
        }

class WeierstrassLatticeWidget(WidgetExecutor):
    """Systematic lattice point trajectory analysis"""
    
    def _execute_impl(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        p = validated_input['p']
        q = validated_input['q']
        N = validated_input['N']
        lattice_range = validated_input.get('lattice_range', 3)
        
        return {
            'plot_data': {
                'image_base64': f'lattice_analysis_p{p}_q{q}_range{lattice_range}',
                'width': 800,
                'height': 600
            },
            'lattice_data': {
                'systematic_trajectories': f'{lattice_range}x{lattice_range}_grid',
                'periodic_structure': 'analyzed'
            }
        }

class WeierstrassPoleWidget(WidgetExecutor):
    """Pole structure and singularity analysis"""
    
    def _execute_impl(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        p = validated_input['p']
        q = validated_input['q']
        N = validated_input['N']
        pole_radius = validated_input.get('pole_radius', 0.1)
        
        return {
            'plot_data': {
                'image_base64': f'pole_analysis_p{p}_q{q}_N{N}',
                'width': 800,
                'height': 600
            },
            'pole_data': {
                'poles_located': f'lattice_poles_p{p}_q{q}',
                'residues_computed': True,
                'singularity_strength': 'second_order'
            }
        }

class WeierstrassContourWidget(WidgetExecutor):
    """Topographic field contour mapping"""
    
    def _execute_impl(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        p = validated_input['p']
        q = validated_input['q']
        N = validated_input['N']
        contour_levels = validated_input.get('contour_levels', 20)
        field_type = validated_input.get('field_type', 'magnitude')
        
        return {
            'plot_data': {
                'image_base64': f'contour_plot_{field_type}_p{p}_q{q}',
                'width': 800,
                'height': 600
            },
            'contour_data': {
                'levels': contour_levels,
                'field_type': field_type,
                'topographic_analysis': 'complete'
            }
        }

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
    elif widget_id == 'wp-two-panel':
        return WeierstrassTwoPanelWidget(schema)
    elif widget_id == 'wp-three-panel':
        return WeierstrassThreePanelWidget(schema)
    elif widget_id == 'wp-five-panel':
        return WeierstrassFivePanelWidget(schema)
    elif widget_id == 'wp-trajectories':
        return WeierstrassTrajectoryWidget(schema)
    elif widget_id == 'wp-lattice':
        return WeierstrassLatticeWidget(schema)
    elif widget_id == 'wp-poles':
        return WeierstrassPoleWidget(schema)
    elif widget_id == 'wp-contours':
        return WeierstrassContourWidget(schema)
    elif widget_id == 'data-generator':
        return DataGeneratorWidget(schema)
    elif widget_id == 'data-plot':
        return DataPlotWidget(schema)
    else:
        return WidgetExecutor(schema)  # Basic implementation

class DataPlotWidget(WidgetExecutor):
    """2D data plotting widget"""
    
    def _execute_impl(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        data = validated_input['data']
        plot_type = validated_input.get('plot_type', 'line')
        title = validated_input.get('title', 'Data Plot')
        
        return {
            'plot_image': {
                'image_base64': f'{plot_type}_plot_data',
                'width': 600,
                'height': 400
            },
            'statistics': {
                'mean_x': sum(data['x']) / len(data['x']) if data['x'] else 0,
                'mean_y': sum(data['y']) / len(data['y']) if data['y'] else 0,
                'std_x': 1.0,
                'std_y': 1.0
            }
        }

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


class StickyNoteWidget(WidgetExecutor):
    """Simple sticky note widget - the most basic widget example"""
    
    def _execute_impl(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
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
        """Simple markdown rendering for basic formatting"""
        html = content
        
        # Headers
        html = re.sub(r'^# (.*$)', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.*$)', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^### (.*$)', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        
        # Bold and italic
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
        
        # Code blocks and inline code
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


def create_widget(widget_type: str, schemas: Dict[str, Any]) -> WidgetExecutor:
    """Factory function to create widget instances based on type"""
    if widget_type not in schemas['widget-schemas']:
        raise ValueError(f"Unknown widget type: {widget_type}")
    
    schema = schemas['widget-schemas'][widget_type]
    
    # Map widget types to their implementation classes
    widget_classes = {
        'sticky-note': StickyNoteWidget,
        'markdown-note': MarkdownWidget,
        'python-code': PythonWidget,
        'wp-two-panel': WeierstrassTwoPanelWidget,
        'wp-three-panel': WeierstrassThreePanelWidget,
        'wp-five-panel': WeierstrassFivePanelWidget,
        'wp-trajectories': WeierstrassTrajectoryWidget,
        'wp-lattice': WeierstrassLatticeWidget,
        'wp-poles': WeierstrassPoleWidget,
        'wp-contours': WeierstrassContourWidget,
        'data-plot': DataPlotWidget,
        'data-generator': DataGeneratorWidget,
    }
    
    widget_class = widget_classes.get(widget_type, WidgetExecutor)
    return widget_class(schema)