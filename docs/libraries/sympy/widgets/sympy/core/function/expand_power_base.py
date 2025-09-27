"""
SymPy expand_power_base Widget
Wrapper around expand that only uses the power_base hint. A wrapper to expand(power_base=True) which separates a power with a base that is a Mul into a product of powers, without performing any other expansions, provided that assumptions about the power's base and exponent allow. deep=False (default is True) will only apply to the top-level expression. force=True (default is False) will cause the expansion to ignore assumptions about the base and exponent. When False, the expansion will only happen if the base is non-negative or the exponent is an integer. >>> from sympy.abc import x, y, z >>> from sympy import expand_power_base, sin, cos, exp, Symbol >>> (x*y)**2 x**2*y**2 >>> (2*x)**y (2*x)**y >>> expand_power_base(_) 2**y*x**y >>> expand_power_base((x*y)**z) (x*y)**z >>> expand_power_base((x*y)**z, force=True) x**z*y**z >>> expand_power_base(sin((x*y)**z), deep=False) sin((x*y)**z) >>> expand_power_base(sin((x*y)**z), force=True) sin(x**z*y**z) >>> expand_power_base((2*sin(x))**y + (2*cos(x))**y) 2**y*sin(x)**y + 2**y*cos(x)**y >>> expand_power_base((2*exp(y))**x) 2**x*exp(y)**x >>> expand_power_base((2*cos(x))**y) 2**y*cos(x)**y Notice that sums are left untouched. If this is not the desired behavior, apply full ``expand()`` to the expression: >>> expand_power_base(((x+y)*z)**2) z**2*(x + y)**2 >>> (((x+y)*z)**2).expand() x**2*z**2 + 2*x*y*z**2 + y**2*z**2 >>> expand_power_base((2*y)**(1+z)) 2**(z + 1)*y**(z + 1) >>> ((2*y)**(1+z)).expand() 2*2**z*y**(z + 1) The power that is unexpanded can be expanded safely when ``y != 0``, otherwise different values might be obtained for the expression: >>> prev = _ If we indicate that ``y`` is positive but then replace it with a value of 0 after expansion, the expression becomes 0: >>> p = Symbol('p', positive=True) >>> prev.subs(y, p).expand().subs(p, 0) 0 But if ``z = -1`` the expression would not be zero: >>> prev.subs(y, 0).subs(z, -1) 1 See Also expand
"""

from typing import Dict, Any
import sympy as sp
from sympy.core.function import expand_power_base


class SymPyExpand_Power_BaseWidget:
    """Widget for SymPy expand_power_base function."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the expand_power_base function."""
        try:
            # Extract parameters from input
            expr = validated_input.get('expr', None)
            deep = validated_input.get('deep', 'True')
            force = validated_input.get('force', 'False')
            
            # Convert string expressions to SymPy objects where needed
            for key, value in locals().items():
                if key in ['expr', 'deep', 'force'] and isinstance(value, str):
                    try:
                        locals()[key] = sp.sympify(value)
                    except:
                        pass  # Keep as string if sympify fails
            
            # Call the SymPy function
            result = expand_power_base(expr, deep, force)
            
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
                    'function': 'expand_power_base',
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
                    'function': 'expand_power_base',
                    'module': 'sympy.core.function'
                }
            }
