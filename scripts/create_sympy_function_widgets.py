#!/usr/bin/env python3
"""
Create SymPy function widgets through introspection of actual SymPy source code.
This script analyzes SymPy modules and creates widgets for each function.
"""

import os
import json
import inspect
import importlib
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import sympy


class SymPyFunctionIntrospector:
    """Introspect SymPy modules to find functions and create widgets."""
    
    def __init__(self, output_dir: str = "docs/libraries/sympy"):
        self.output_dir = Path(output_dir)
        self.modules_analyzed = {}
        self.functions_found = {}
        self.widgets_created = {}
        
    def analyze_module(self, module_path: str) -> Dict[str, Any]:
        """Analyze a SymPy module to find functions."""
        try:
            module = importlib.import_module(module_path)
            module_info = {
                'path': module_path,
                'name': module.__name__,
                'doc': getattr(module, '__doc__', ''),
                'functions': {}
            }
            
            # Find all callable functions (not classes) in the module
            for name in dir(module):
                if name.startswith('_'):
                    continue
                    
                obj = getattr(module, name)
                
                # Only include actual functions, not classes or imports
                if (inspect.isfunction(obj) and 
                    hasattr(obj, '__module__') and 
                    obj.__module__ == module.__name__):
                    
                    func_info = self.analyze_function(obj, name)
                    if func_info:
                        module_info['functions'][name] = func_info
            
            return module_info
            
        except ImportError as e:
            print(f"Could not import {module_path}: {e}")
            return None
    
    def analyze_function(self, func, name: str) -> Optional[Dict[str, Any]]:
        """Analyze a function to extract widget information."""
        try:
            sig = inspect.signature(func)
            doc = func.__doc__ or ""
            
            # Parse docstring to extract parameter info
            param_info = self.parse_docstring(doc)
            
            func_info = {
                'name': name,
                'signature': str(sig),
                'docstring': doc,
                'parameters': {},
                'returns': param_info.get('returns', {}),
                'examples': param_info.get('examples', []),
                'description': param_info.get('description', doc.split('\n')[0] if doc else f"SymPy {name} function")
            }
            
            # Analyze parameters
            for param_name, param in sig.parameters.items():
                param_info_parsed = param_info.get('parameters', {}).get(param_name, {})
                
                func_info['parameters'][param_name] = {
                    'name': param_name,
                    'type': self.infer_parameter_type(param, param_info_parsed),
                    'description': param_info_parsed.get('description', ''),
                    'default': str(param.default) if param.default != inspect.Parameter.empty else None,
                    'required': param.default == inspect.Parameter.empty
                }
            
            return func_info
            
        except Exception as e:
            print(f"Error analyzing function {name}: {e}")
            return None
    
    def parse_docstring(self, docstring: str) -> Dict[str, Any]:
        """Parse SymPy-style docstring to extract parameter and return information."""
        if not docstring:
            return {}
        
        lines = [line.rstrip() for line in docstring.split('\n')]
        result = {
            'description': '',
            'parameters': {},
            'returns': {},
            'examples': []
        }
        
        # Find section boundaries
        sections = {}
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped in ['Parameters', 'Returns', 'Examples', 'References'] and \
               i + 1 < len(lines) and lines[i + 1].strip().startswith('==='):
                sections[stripped.lower()] = i + 2  # Start after the === line
        
        # Extract description (everything before Parameters section)
        desc_end = sections.get('parameters', len(lines)) - 2 if 'parameters' in sections else len(lines)
        desc_lines = []
        for i in range(desc_end):
            line = lines[i].strip()
            if line and not line.startswith('==='):
                desc_lines.append(line)
        
        if desc_lines:
            result['description'] = ' '.join(desc_lines)
        
        # Parse Parameters section
        if 'parameters' in sections:
            start_idx = sections['parameters']
            end_idx = min([sections.get(s, len(lines)) - 2 for s in ['returns', 'examples', 'references'] 
                          if s in sections] + [len(lines)])
            
            current_param = None
            param_desc_lines = []
            
            for i in range(start_idx, end_idx):
                if i >= len(lines):
                    break
                line = lines[i]
                stripped = line.strip()
                
                # Skip empty lines 
                if not stripped:
                    continue
                    
                # Stop if we hit another section
                if stripped in ['Returns', 'Examples', 'References']:
                    break
                
                # Check for parameter definition (name : type)
                if ':' in stripped and len(line) - len(line.lstrip()) <= 4:  # Allow up to 4 spaces of indentation
                    # Save previous parameter
                    if current_param:
                        result['parameters'][current_param]['description'] = ' '.join(param_desc_lines).strip()
                    
                    # Parse new parameter
                    parts = stripped.split(':', 1)
                    if len(parts) == 2:
                        param_name = parts[0].strip()
                        param_type = parts[1].strip()
                        current_param = param_name
                        param_desc_lines = []
                        
                        result['parameters'][param_name] = {
                            'type': param_type,
                            'description': ''
                        }
                elif current_param and (line.startswith('        ') or line.startswith('\t\t')):  # Description indented more
                    # Parameter description line
                    if stripped and not stripped.startswith('..'):  # Skip reStructuredText directives
                        param_desc_lines.append(stripped)
            
            # Save last parameter
            if current_param:
                result['parameters'][current_param]['description'] = ' '.join(param_desc_lines).strip()
        
        # Parse Returns section
        if 'returns' in sections:
            start_idx = sections['returns']
            end_idx = min([sections.get(s, len(lines)) - 2 for s in ['examples', 'references'] 
                          if s in sections] + [len(lines)])
            
            for i in range(start_idx, end_idx):
                if i >= len(lines):
                    break
                line = lines[i]
                stripped = line.strip()
                
                if ':' in stripped and not line.startswith('    '):
                    parts = stripped.split(':', 1)
                    if len(parts) == 2:
                        return_name = parts[0].strip()
                        return_type = parts[1].strip()
                        result['returns'] = {
                            'name': return_name,
                            'type': return_type,
                            'description': ''
                        }
                        break
        
        # Parse Examples section
        if 'examples' in sections:
            start_idx = sections['examples']
            end_idx = sections.get('references', len(lines)) - 2 if 'references' in sections else len(lines)
            
            for i in range(start_idx, end_idx):
                if i >= len(lines):
                    break
                line = lines[i].strip()
                if line and not line.startswith('===') and line != 'References':
                    result['examples'].append(line)
        
        return result
    
    def infer_parameter_type(self, param: inspect.Parameter, param_info: Dict[str, str]) -> str:
        """Infer JSON schema type from parameter information."""
        param_type = param_info.get('type', '').lower()
        
        if 'expr' in param_type or 'expression' in param_type:
            return 'string'
        elif 'symbol' in param_type or 'var' in param_type:
            return 'string'  
        elif 'list' in param_type or 'iterable' in param_type:
            return 'array'
        elif 'bool' in param_type or 'boolean' in param_type:
            return 'boolean'
        elif 'int' in param_type or 'integer' in param_type:
            return 'integer'
        elif 'float' in param_type or 'number' in param_type:
            return 'number'
        elif 'function' in param_type:
            return 'string'  # Function as string expression
        else:
            return 'string'  # Default to string for SymPy expressions
    
    def create_widget_schema(self, module_info: Dict[str, Any], func_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create JSON schema for a function widget."""
        func_name = func_info['name']
        module_path = module_info['path']
        
        # Create input schema
        input_properties = {}
        required = []
        
        for param_name, param_info in func_info['parameters'].items():
            prop = {
                'type': param_info['type'],
                'description': param_info['description'] or f"Parameter {param_name}"
            }
            
            # Set better defaults based on parameter name and type
            if param_info['default'] is not None and param_info['default'] != 'None':
                if param_info['type'] == 'string':
                    prop['default'] = str(param_info['default']).strip("'\"")
                elif param_info['type'] == 'boolean':
                    prop['default'] = param_info['default'].lower() == 'true'
                elif param_info['type'] == 'array':
                    prop['default'] = []
            else:
                # Set sensible defaults for common SymPy parameters
                if param_name.lower() in ['l', 'expr', 'expression', 'f']:
                    prop['default'] = "x**2 + y**2"  # Example Lagrangian or expression
                elif param_name.lower() in ['funcs', 'functions']:
                    prop['default'] = ["x(t)"]
                    prop['items'] = {'type': 'string'}
                elif param_name.lower() in ['vars', 'variables', 'symbols']:
                    prop['default'] = ["t"]
                    prop['items'] = {'type': 'string'}
                elif param_info['type'] == 'array':
                    prop['default'] = []
                    prop['items'] = {'type': 'string'}
                elif param_info['type'] == 'boolean':
                    prop['default'] = False
                elif param_info['type'] == 'string':
                    prop['default'] = ""
            
            input_properties[param_name] = prop
            
            if param_info['required']:
                required.append(param_name)
        
        # Create widget schema
        widget_schema = {
            'id': f'sympy-{module_path.replace(".", "-")}-{func_name}',
            'name': f'SymPy {func_name}',
            'description': func_info['description'],
            'category': 'sympy',
            'module': module_path,
            'function': func_name,
            'icon': '🧮',
            'input_schema': {
                'type': 'object',
                'properties': input_properties,
                'required': required,
                'additionalProperties': False
            },
            'output_schema': {
                'type': 'object',
                'properties': {
                    'result': {
                        'type': 'string',
                        'description': 'Result of the computation'
                    },
                    'latex': {
                        'type': 'string',
                        'description': 'LaTeX representation of the result'
                    },
                    'metadata': {
                        'type': 'object',
                        'description': 'Additional metadata about the computation'
                    }
                },
                'required': ['result']
            }
        }
        
        return widget_schema
    
    def create_widget_implementation(self, module_info: Dict[str, Any], func_info: Dict[str, Any]) -> str:
        """Create Python implementation for a function widget."""
        func_name = func_info['name']
        module_path = module_info['path']
        class_name = f'SymPy{func_name.title()}Widget'
        
        # Generate parameter processing code
        param_processing = []
        for param_name, param_info in func_info['parameters'].items():
            if param_info['type'] == 'array':
                param_processing.append(f"            {param_name} = validated_input.get('{param_name}', [])")
            elif param_info['type'] == 'boolean':
                default = 'True' if param_info.get('default') == 'True' else 'False'
                param_processing.append(f"            {param_name} = validated_input.get('{param_name}', {default})")
            else:
                default = repr(param_info.get('default', ''))
                param_processing.append(f"            {param_name} = validated_input.get('{param_name}', {default})")
        
        param_processing_code = '\n'.join(param_processing)
        
        # Generate function call
        param_names = list(func_info['parameters'].keys())
        if param_names:
            func_call = f"result = {func_name}({', '.join(param_names)})"
        else:
            func_call = f"result = {func_name}()"
        
        implementation = f'''"""
SymPy {func_name} Widget
{func_info['description']}
"""

from typing import Dict, Any
import sympy as sp
from {module_path} import {func_name}


class {class_name}:
    """Widget for SymPy {func_name} function."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the {func_name} function."""
        try:
            # Extract parameters from input
{param_processing_code}
            
            # Convert string expressions to SymPy objects where needed
            for key, value in locals().items():
                if key in {repr(list(func_info['parameters'].keys()))} and isinstance(value, str):
                    try:
                        locals()[key] = sp.sympify(value)
                    except:
                        pass  # Keep as string if sympify fails
            
            # Call the SymPy function
            {func_call}
            
            # Format output
            result_str = str(result)
            try:
                latex_str = sp.latex(result) if hasattr(result, '_latex') or hasattr(sp, 'latex') else result_str
            except:
                latex_str = result_str
            
            return {{
                'result': result_str,
                'latex': latex_str,
                'metadata': {{
                    'function': '{func_name}',
                    'module': '{module_path}',
                    'result_type': type(result).__name__,
                    'parameters_used': validated_input
                }}
            }}
            
        except Exception as e:
            return {{
                'result': f"Error: {{str(e)}}",
                'latex': "\\\\text{{Error}}",
                'metadata': {{
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'function': '{func_name}',
                    'module': '{module_path}'
                }}
            }}
'''
        
        return implementation
    
    def process_modules(self, module_paths: List[str]):
        """Process multiple SymPy modules to create widgets."""
        all_schemas = {}
        
        for module_path in module_paths:
            print(f"Analyzing module: {module_path}")
            module_info = self.analyze_module(module_path)
            
            if not module_info or not module_info['functions']:
                print(f"  No functions found in {module_path}")
                continue
            
            print(f"  Found {len(module_info['functions'])} functions")
            
            # Create widgets for each function
            for func_name, func_info in module_info['functions'].items():
                print(f"    Creating widget for {func_name}")
                
                # Create schema
                widget_schema = self.create_widget_schema(module_info, func_info)
                all_schemas[widget_schema['id']] = widget_schema
                
                # Create implementation file
                implementation = self.create_widget_implementation(module_info, func_info)
                
                # Create directory structure
                module_parts = module_path.split('.')[1:]  # Remove 'sympy' prefix
                widget_dir = self.output_dir / 'widgets' / 'sympy' / '/'.join(module_parts)
                widget_dir.mkdir(parents=True, exist_ok=True)
                
                # Write implementation file
                widget_file = widget_dir / f'{func_name}.py'
                with open(widget_file, 'w') as f:
                    f.write(implementation)
        
        # Write combined schema file
        schema_output = {
            'widget-schemas': all_schemas
        }
        
        schema_file = self.output_dir / 'function_widget_schemas.json'
        with open(schema_file, 'w') as f:
            json.dump(schema_output, f, indent=2)
        
        print(f"\nCreated {len(all_schemas)} function widgets")
        print(f"Schema file: {schema_file}")
        
        return all_schemas


def main():
    """Main function to create SymPy function widgets."""
    introspector = SymPyFunctionIntrospector()
    
    # List of SymPy modules to analyze
    modules_to_analyze = [
        'sympy.calculus.euler',
        'sympy.calculus.util',
        'sympy.core.function',
        'sympy.functions.elementary.trigonometric',
        'sympy.functions.elementary.exponential',
        'sympy.functions.elementary.hyperbolic',
        'sympy.functions.elementary.integers',
        'sympy.functions.elementary.miscellaneous',
        'sympy.functions.special.gamma_functions',
        'sympy.functions.special.bessel',
        'sympy.simplify.simplify',
        'sympy.solve.solve',
        'sympy.matrices.common',
        'sympy.geometry.point',
        'sympy.geometry.line',
        'sympy.geometry.polygon',
        'sympy.geometry.ellipse',
        'sympy.plotting.plot'
    ]
    
    # Process modules
    schemas = introspector.process_modules(modules_to_analyze)
    
    print("\n" + "="*50)
    print("SymPy Function Widget Generation Complete!")
    print(f"Total widgets created: {len(schemas)}")
    print("="*50)


if __name__ == "__main__":
    main()