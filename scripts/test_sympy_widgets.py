#!/usr/bin/env python3
"""
Test script for SymPy widgets
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'docs', 'weierstrass-playground', 'widgets'))

from widget_executor import create_widget
import json

def test_sympy_widgets():
    """Test SymPy widget functionality."""
    
    # Load widget schemas
    with open('docs/weierstrass-playground/widget-schemas.json', 'r') as f:
        schemas = json.load(f)
    
    print("🧪 Testing SymPy Widgets...")
    print("")
    
    # Test SymPy Add widget
    print("Testing SymPy Add widget:")
    try:
        add_widget = create_widget('sympy-core-add', schemas)
        result = add_widget.execute({'expression': 'x + y + 2'})
        print(f"  Input: x + y + 2")
        print(f"  Result: {result['result']}")
        print(f"  LaTeX: {result['latex']}")
        print("  ✅ Success")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    print()
    
    # Test SymPy Elementary Functions widget
    print("Testing SymPy Elementary Functions widget:")
    try:
        func_widget = create_widget('sympy-functions-elementary', schemas)
        result = func_widget.execute({'expression': 'sin(x) + cos(x)'})
        print(f"  Input: sin(x) + cos(x)")
        print(f"  Result: {result['result']}")
        print(f"  LaTeX: {result['latex']}")
        print("  ✅ Success")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    print()
    
    # Test SymPy Matrix widget
    print("Testing SymPy Matrix widget:")
    try:
        matrix_widget = create_widget('sympy-matrices-dense', schemas)
        result = matrix_widget.execute({'expression': '[[1, 2], [3, 4]]'})
        print(f"  Input: [[1, 2], [3, 4]]")
        print(f"  Result: {result['result']}")
        print(f"  LaTeX: {result['latex']}")
        print("  ✅ Success")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    print()
    print("🎉 SymPy widget testing completed!")

if __name__ == "__main__":
    os.chdir("/home/runner/work/notebooks/notebooks")
    test_sympy_widgets()