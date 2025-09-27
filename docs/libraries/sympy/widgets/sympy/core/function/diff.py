"""
SymPy diff Widget
Differentiate f with respect to symbols. Explanation This is just a wrapper to unify .diff() and the Derivative class; its interface is similar to that of integrate().  You can use the same shortcuts for multiple variables as with Derivative.  For example, diff(f(x), x, x, x) and diff(f(x), x, 3) both return the third derivative of f(x). You can pass evaluate=False to get an unevaluated Derivative class.  Note that if there are 0 symbols (such as diff(f(x), x, 0), then the result will be the function (the zeroth derivative), even if evaluate=False. Examples >>> from sympy import sin, cos, Function, diff >>> from sympy.abc import x, y >>> f = Function('f') >>> diff(sin(x), x) cos(x) >>> diff(f(x), x, x, x) Derivative(f(x), (x, 3)) >>> diff(f(x), x, 3) Derivative(f(x), (x, 3)) >>> diff(sin(x)*cos(y), x, 2, y, 2) sin(x)*cos(y) >>> type(diff(sin(x), x)) cos >>> type(diff(sin(x), x, evaluate=False)) <class 'sympy.core.function.Derivative'> >>> type(diff(sin(x), x, 0)) sin >>> type(diff(sin(x), x, 0, evaluate=False)) sin >>> diff(sin(x)) cos(x) >>> diff(sin(x*y)) Traceback (most recent call last): ... ValueError: specify differentiation variables to differentiate sin(x*y) Note that ``diff(sin(x))`` syntax is meant only for convenience in interactive sessions and should be avoided in library code. References .. [1] https://reference.wolfram.com/legacy/v5_2/Built-inFunctions/AlgebraicComputation/Calculus/D.html See Also Derivative idiff: computes the derivative implicitly
"""

from typing import Dict, Any
import sympy as sp
from sympy.core.function import diff


class SymPyDiffWidget:
    """Widget for SymPy diff function."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the diff function."""
        try:
            # Extract parameters from input
            f = validated_input.get('f', None)
            symbols = validated_input.get('symbols', None)
            kwargs = validated_input.get('kwargs', None)
            
            # Convert string expressions to SymPy objects where needed
            for key, value in locals().items():
                if key in ['f', 'symbols', 'kwargs'] and isinstance(value, str):
                    try:
                        locals()[key] = sp.sympify(value)
                    except:
                        pass  # Keep as string if sympify fails
            
            # Call the SymPy function
            result = diff(f, symbols, kwargs)
            
            # Format output
            result_str = str(result)
            try:
                latex_str = sp.latex(result) if hasattr(result, '_latex') or hasattr(sp, 'latex') else result_str
            except:
                latex_str = result_str
            
            return {
                'result': result_str,
                'latex': latex_str,
                'metadata': {
                    'function': 'diff',
                    'module': 'sympy.core.function',
                    'result_type': type(result).__name__,
                    'parameters_used': validated_input
                }
            }
            
        except Exception as e:
            return {
                'result': f"Error: {str(e)}",
                'latex': "\\text{Error}",
                'metadata': {
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'function': 'diff',
                    'module': 'sympy.core.function'
                }
            }
