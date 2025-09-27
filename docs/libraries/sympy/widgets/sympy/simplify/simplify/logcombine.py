"""
SymPy logcombine Widget
Takes logarithms and combines them using the following rules: - log(x) + log(y) == log(x*y) if both are positive - a*log(x) == log(x**a) if x is positive and a is real If ``force`` is ``True`` then the assumptions above will be assumed to hold if there is no assumption already in place on a quantity. For example, if ``a`` is imaginary or the argument negative, force will not perform a combination but if ``a`` is a symbol with no assumptions the change will take place. Examples >>> from sympy import Symbol, symbols, log, logcombine, I >>> from sympy.abc import a, x, y, z >>> logcombine(a*log(x) + log(y) - log(z)) a*log(x) + log(y) - log(z) >>> logcombine(a*log(x) + log(y) - log(z), force=True) log(x**a*y/z) >>> x,y,z = symbols('x,y,z', positive=True) >>> a = Symbol('a', real=True) >>> logcombine(a*log(x) + log(y) - log(z)) log(x**a*y/z) The transformation is limited to factors and/or terms that contain logs, so the result depends on the initial state of expansion: >>> eq = (2 + 3*I)*log(x) >>> logcombine(eq, force=True) == eq True >>> logcombine(eq.expand(), force=True) log(x**2) + I*log(x**3) See Also posify: replace all symbols with symbols having positive assumptions sympy.core.function.expand_log: expand the logarithms of products and powers; the opposite of logcombine
"""

from typing import Dict, Any
import sympy as sp
from sympy.simplify.simplify import logcombine


class SymPyLogcombineWidget:
    """Widget for SymPy logcombine function."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the logcombine function."""
        try:
            # Extract parameters from input
            expr = validated_input.get('expr', None)
            force = validated_input.get('force', 'False')
            
            # Convert string expressions to SymPy objects where needed
            for key, value in locals().items():
                if key in ['expr', 'force'] and isinstance(value, str):
                    try:
                        locals()[key] = sp.sympify(value)
                    except:
                        pass  # Keep as string if sympify fails
            
            # Call the SymPy function
            result = logcombine(expr, force)
            
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
                    'function': 'logcombine',
                    'module': 'sympy.simplify.simplify',
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
                    'function': 'logcombine',
                    'module': 'sympy.simplify.simplify'
                }
            }
