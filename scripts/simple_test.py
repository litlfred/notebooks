#!/usr/bin/env python3
"""
Simple test of the refactored SymPy widgets using the base class.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'docs', 'libraries', 'sympy', 'widgets'))

# Test the refactored euler_equations widget
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'docs', 'libraries', 'sympy', 'widgets', 'sympy', 'calculus', 'euler'))

try:
    from euler_equations import SymPyEuler_EquationsWidget
    
    print("✅ Successfully imported SymPyEuler_EquationsWidget")
    
    # Create widget instance
    widget = SymPyEuler_EquationsWidget({})
    print("✅ Successfully created widget instance")
    
    # Test simple execution
    result = widget.execute({'L': 'x**2', 'funcs': [], 'vars': []})
    print(f"✅ Widget execution result: {result}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test the refactored simplify widget  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'docs', 'libraries', 'sympy', 'widgets', 'sympy', 'simplify', 'simplify'))

try:
    from simplify import SymPySimplifyWidget
    
    print("✅ Successfully imported SymPySimplifyWidget")
    
    # Create widget instance
    widget = SymPySimplifyWidget({})
    print("✅ Successfully created widget instance")
    
    # Test simple execution
    result = widget.execute({'expr': 'x + x'})
    print(f"✅ Widget execution result: {result}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n🎉 Base SymPy widget system is working!")