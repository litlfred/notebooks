#!/usr/bin/env python3
"""
Fix the hierarchical class names to follow proper convention.
"""

import os
import glob
import re

def fix_widget_class_names():
    """Fix all SymPy widget class names to proper hierarchical convention."""
    
    # Find all SymPy widget files
    widget_files = glob.glob('/home/runner/work/notebooks/notebooks/docs/libraries/sympy/widgets/sympy/**/*.py', recursive=True)
    
    updated_files = []
    
    for file_path in widget_files:
        if 'base_sympy_widget.py' in file_path:
            continue
            
        # Read file content
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Track if any changes were made
        original_content = content
        
        # Extract the proper hierarchical name from file path
        path_parts = file_path.split('/')
        if 'sympy' in path_parts:
            sympy_index = path_parts.index('sympy')
            module_parts = path_parts[sympy_index+1:-1]  # Exclude 'sympy' and file name
            file_name = path_parts[-1].replace('.py', '')
            
            # Create proper hierarchical name
            # Convert snake_case to CamelCase and combine
            all_parts = ['SymPy']
            for part in module_parts:
                all_parts.append(part.replace('_', '').title())
            all_parts.append(file_name.replace('_', '').title())
            proper_class_name = ''.join(all_parts) + 'Widget'
            
            # Find existing class definition
            class_pattern = r'class (SymPy\w+Widget)\(BaseSymPyWidget\):'
            match = re.search(class_pattern, content)
            
            if match:
                current_class_name = match.group(1)
                if current_class_name != proper_class_name:
                    # Replace the class name
                    content = content.replace(f'class {current_class_name}(BaseSymPyWidget):', 
                                            f'class {proper_class_name}(BaseSymPyWidget):')
                    print(f"Fixed: {current_class_name} -> {proper_class_name} in {file_path}")
        
        # Write back if changed
        if content != original_content:
            with open(file_path, 'w') as f:
                f.write(content)
            updated_files.append(file_path)
    
    return updated_files

if __name__ == "__main__":
    updated_files = fix_widget_class_names()
    print(f"\nFixed {len(updated_files)} widget files with proper hierarchical class names.")
    
    # Show examples of the proper naming convention
    print("\nExamples of proper hierarchical names:")
    examples = [
        "docs/libraries/sympy/widgets/sympy/calculus/euler/euler_equations.py -> SymPyCalculusEulerEulerEquationsWidget",
        "docs/libraries/sympy/widgets/sympy/core/function/expand.py -> SymPyCoreFunctionExpandWidget", 
        "docs/libraries/sympy/widgets/sympy/simplify/simplify/simplify.py -> SymPySimplifySimplifySimplifyWidget"
    ]
    for example in examples:
        print(f"  {example}")