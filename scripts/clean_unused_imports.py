#!/usr/bin/env python3
"""
Clean up unused imports in SymPy widgets
"""

import os
import glob

def clean_unused_imports(widget_file):
    """Remove unused sys import from widget files"""
    with open(widget_file, 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    new_lines = []
    
    for line in lines:
        # Skip standalone sys import if it's not used elsewhere
        if line.strip() == 'import sys':
            # Check if sys is used elsewhere in the file
            if 'sys.' not in content.replace(line, ''):
                continue
        new_lines.append(line)
    
    # Remove extra empty lines
    while len(new_lines) > 1 and new_lines[0] == '' and new_lines[1] == '':
        new_lines.pop(0)
    
    content = '\n'.join(new_lines)
    
    with open(widget_file, 'w') as f:
        f.write(content)
    
    print(f"Cleaned: {widget_file}")

def main():
    # Find all widget Python files
    widget_pattern = '/home/runner/work/notebooks/notebooks/docs/libraries/sympy/widgets/sympy/**/*.py'
    widget_files = glob.glob(widget_pattern, recursive=True)
    
    print(f"Found {len(widget_files)} widget files to clean")
    
    for widget_file in widget_files:
        clean_unused_imports(widget_file)
    
    print("All widget files have been cleaned")

if __name__ == "__main__":
    main()