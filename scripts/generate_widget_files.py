#!/usr/bin/env python3
"""
Script to generate Python widget implementations for SymPy widgets
"""

import json
from pathlib import Path
import os

def load_widget_schemas():
    """Load the generated widget schemas."""
    schema_path = Path("docs/sympy/widget_schemas.json")
    with open(schema_path, 'r') as f:
        return json.load(f)

def generate_widget_template(widget_id, schema):
    """Generate a Python widget implementation template."""
    
    class_name = schema.get('class_name', 'Unknown')
    method_name = schema.get('method_name', None)
    module_name = schema.get('module_name', 'sympy')
    
    if method_name:
        # This is a method widget
        widget_class_name = f"SymPy{class_name}{method_name.capitalize()}Widget"
        description = f"Widget for SymPy {class_name}.{method_name} method"
    else:
        # This is a class widget
        widget_class_name = f"SymPy{class_name}Widget"
        description = f"Widget for SymPy {class_name} class"
    
    # Clean up class name
    widget_class_name = widget_class_name.replace('-', '').replace('_', '')
    
    # Build method metadata line
    method_line = f"                    'method_name': '{method_name}'," if method_name else ""
    
    template = f'''"""
{description}
"""

from typing import Dict, Any
import sympy as sp


class {widget_class_name}:
    """Widget for SymPy {class_name}{"." + method_name if method_name else ""} operations."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the {class_name}{"." + method_name if method_name else ""} operation."""
        try:
            # Parse input parameters
            expression_str = validated_input.get('expression', 'x')
            
            # Parse SymPy expression
            expr = sp.sympify(expression_str)
            
            # Apply operation based on widget type
            if "{method_name}" and hasattr(expr, "{method_name}"):
                # Method widget - call method on expression
                method = getattr(expr, "{method_name}")
                result = method()
            else:
                # Class widget or generic operation
                result = expr
            
            # Format output
            result_str = str(result)
            latex_str = sp.latex(result)
            
            return {{
                'result': result_str,
                'latex': latex_str,
                'metadata': {{
                    'widget_id': '{widget_id}',
                    'class_name': '{class_name}',
{method_line}
                    'module_name': '{module_name}',
                    'result_type': type(result).__name__
                }}
            }}
            
        except Exception as e:
            return {{
                'result': f"Error: {{str(e)}}",
                'latex': "\\\\text{{Error}}",
                'metadata': {{
                    'error': str(e),
                    'widget_id': '{widget_id}',
                    'error_type': type(e).__name__
                }}
            }}
'''
    
    return template

def generate_widget_files():
    """Generate Python files for all SymPy widgets."""
    schemas = load_widget_schemas()
    widgets_dir = Path("docs/sympy/widgets")
    widgets_dir.mkdir(exist_ok=True)
    
    generated_count = 0
    
    for widget_id, schema in schemas['widget-schemas'].items():
        if not widget_id.startswith('sympy-'):
            continue
            
        # Parse widget ID to create hierarchical structure
        # Example: sympy-core-add -> sympy/core/add.py
        parts = widget_id.split('-')
        if len(parts) >= 3 and parts[0] == 'sympy':
            module_path = '/'.join(parts[1:-1])  # e.g., 'core' 
            class_name = parts[-1]  # e.g., 'add'
            
            # Create directory structure
            module_dir = widgets_dir / 'sympy' / module_path
            module_dir.mkdir(parents=True, exist_ok=True)
            
            filename = f"{class_name}.py"
            filepath = module_dir / filename
        else:
            # Fallback to flat structure for unknown patterns
            filename = f"{widget_id.replace('-', '_')}.py"
            filepath = widgets_dir / filename
        
        if filepath.exists():
            print(f"Skipping existing widget: {filename}")
            continue
        
        # Generate template
        template = generate_widget_template(widget_id, schema)
        
        # Write to file
        with open(filepath, 'w') as f:
            f.write(template)
        
        print(f"Generated widget: {filename}")
        generated_count += 1
    
    print(f"\\nGenerated {generated_count} widget files")

if __name__ == "__main__":
    os.chdir("/home/runner/work/notebooks/notebooks")
    generate_widget_files()