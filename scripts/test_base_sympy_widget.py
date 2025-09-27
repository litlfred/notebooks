#!/usr/bin/env python3
"""
Test script to verify that the BaseSymPyWidget class works correctly
with different SymPy functions and parameter types.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'docs', 'libraries', 'sympy', 'widgets'))

from base_sympy_widget import BaseSymPyWidget, SymPyFunctionWidget
from sympy import simplify, expand, symbols
from sympy.core.function import diff
from sympy.calculus.euler import euler_equations


def test_simplify_widget():
    """Test the simplify widget with BaseSymPyWidget."""
    print("Testing simplify widget...")
    
    # Create widget
    widget = SymPyFunctionWidget(
        schema={},
        sympy_function=simplify,
        function_name='simplify',
        module_name='sympy.simplify.simplify'
    )
    
    # Test with a simple expression
    test_input = {
        'expr': 'x**2 + 2*x + 1'
    }
    
    result = widget.execute(test_input)
    print(f"Input: {test_input['expr']}")
    print(f"Result: {result['result']}")
    print(f"LaTeX: {result['latex']}")
    print(f"Status: {'✅' if 'error' not in result['result'].lower() else '❌'}")
    print()
    
    return 'error' not in result['result'].lower()


def test_diff_widget():
    """Test the diff widget with BaseSymPyWidget."""
    print("Testing diff widget...")
    
    # Create widget
    widget = SymPyFunctionWidget(
        schema={},
        sympy_function=diff,
        function_name='diff',
        module_name='sympy.core.function'
    )
    
    # Test with a simple expression
    test_input = {
        'f': 'x**3 + 2*x**2 + x',
        'x': 'x'
    }
    
    result = widget.execute(test_input)
    print(f"Input: diff({test_input['f']}, {test_input['x']})")
    print(f"Result: {result['result']}")
    print(f"LaTeX: {result['latex']}")
    print(f"Status: {'✅' if 'error' not in result['result'].lower() else '❌'}")
    print()
    
    return 'error' not in result['result'].lower()


def test_euler_equations_widget():
    """Test the euler_equations widget."""
    print("Testing euler_equations widget...")
    
    # Create widget
    widget = SymPyFunctionWidget(
        schema={},
        sympy_function=euler_equations,
        function_name='euler_equations',
        module_name='sympy.calculus.euler'
    )
    
    # Test with a simple Lagrangian
    test_input = {
        'L': '(x(t).diff(t))**2/2 - x(t)**2/2',
        'funcs': 'x(t)',
        'vars': 't'
    }
    
    result = widget.execute(test_input)
    print(f"Input: L={test_input['L']}")
    print(f"Result: {result['result']}")
    print(f"Status: {'✅' if 'error' not in result['result'].lower() else '❌'}")
    print()
    
    return 'error' not in result['result'].lower()


def test_parameter_conversion():
    """Test parameter conversion functionality."""
    print("Testing parameter conversion...")
    
    widget = SymPyFunctionWidget(
        schema={},
        sympy_function=expand,
        function_name='expand',
        module_name='sympy'
    )
    
    # Test with different parameter types
    test_cases = [
        {'expr': '(x + 1)**2'},  # String expression
        {'expr': 'sin(x)**2'},   # String with functions
    ]
    
    success_count = 0
    for i, test_input in enumerate(test_cases):
        result = widget.execute(test_input)
        success = 'error' not in result['result'].lower()
        print(f"Test {i+1}: {test_input} -> {'✅' if success else '❌'}")
        if success:
            success_count += 1
    
    print(f"Parameter conversion: {success_count}/{len(test_cases)} tests passed")
    print()
    
    return success_count == len(test_cases)


def main():
    """Run all tests."""
    print("Testing BaseSymPyWidget functionality...")
    print("=" * 50)
    
    tests = [
        test_simplify_widget,
        test_diff_widget,
        test_euler_equations_widget,
        test_parameter_conversion
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"Test failed with exception: {e}")
    
    print("=" * 50)
    print(f"Tests passed: {passed}/{len(tests)}")
    
    if passed == len(tests):
        print("🎉 All tests passed! BaseSymPyWidget is working correctly.")
    else:
        print("❌ Some tests failed. Check the output above.")
    
    return passed == len(tests)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)