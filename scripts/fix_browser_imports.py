#!/usr/bin/env python3
"""
Fix browser compatibility issues in all SymPy widgets by removing file system operations
"""

import os
import re
import glob

def fix_widget_imports(widget_file):
    """Fix imports in a widget file to be browser-compatible"""
    with open(widget_file, 'r') as f:
        content = f.read()
    
    # Remove problematic sys.path manipulation
    lines = content.split('\n')
    new_lines = []
    skip_next = False
    
    for i, line in enumerate(lines):
        # Skip sys.path insert lines and related imports
        if 'sys.path.insert(' in line or skip_next:
            skip_next = False
            continue
        elif line.startswith('import sys') or line.startswith('import os'):
            # Check if next line is the sys.path.insert
            if i + 1 < len(lines) and 'sys.path.insert(' in lines[i + 1]:
                skip_next = True
                continue
        
        new_lines.append(line)
    
    content = '\n'.join(new_lines)
    
    # Fix the base widget import to be browser-compatible
    content = re.sub(
        r'from base_sympy_widget import BaseSymPyWidget',
        '''try:
    from ...base_sympy_widget import BaseSymPyWidget
except ImportError:
    try:
        from ..base_sympy_widget import BaseSymPyWidget
    except ImportError:
        from base_sympy_widget import BaseSymPyWidget''',
        content
    )
    
    # Remove empty lines at the beginning that result from removed imports
    lines = content.split('\n')
    while lines and not lines[0].strip():
        lines.pop(0)
    
    content = '\n'.join(lines)
    
    # Write back the fixed content
    with open(widget_file, 'w') as f:
        f.write(content)
    
    print(f"Fixed: {widget_file}")

def main():
    # Find all widget Python files
    widget_pattern = '/home/runner/work/notebooks/notebooks/docs/libraries/sympy/widgets/sympy/**/*.py'
    widget_files = glob.glob(widget_pattern, recursive=True)
    
    print(f"Found {len(widget_files)} widget files to fix")
    
    for widget_file in widget_files:
        fix_widget_imports(widget_file)
    
    print("All widget files have been fixed for browser compatibility")

if __name__ == "__main__":
    main()