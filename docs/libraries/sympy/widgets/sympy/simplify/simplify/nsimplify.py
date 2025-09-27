"""
SymPy nsimplify Widget
Find a simple representation for a number or, if there are free symbols or if ``rational=True``, then replace Floats with their Rational equivalents. If no change is made and rational is not False then Floats will at least be converted to Rationals. Explanation For numerical expressions, a simple formula that numerically matches the given numerical expression is sought (and the input should be possible to evalf to a precision of at least 30 digits). Optionally, a list of (rationally independent) constants to include in the formula may be given. A lower tolerance may be set to find less exact matches. If no tolerance is given then the least precise value will set the tolerance (e.g. Floats default to 15 digits of precision, so would be tolerance=10**-15). With ``full=True``, a more extensive search is performed (this is useful to find simpler numbers when the tolerance is set low). When converting to rational, if rational_conversion='base10' (the default), then convert floats to rationals using their base-10 (string) representation. When rational_conversion='exact' it uses the exact, base-2 representation. Examples >>> from sympy import nsimplify, sqrt, GoldenRatio, exp, I, pi >>> nsimplify(4/(1+sqrt(5)), [GoldenRatio]) -2 + 2*GoldenRatio >>> nsimplify((1/(exp(3*pi*I/5)+1))) 1/2 - I*sqrt(sqrt(5)/10 + 1/4) >>> nsimplify(I**I, [pi]) exp(-pi/2) >>> nsimplify(pi, tolerance=0.01) 22/7 >>> nsimplify(0.333333333333333, rational=True, rational_conversion='exact') 6004799503160655/18014398509481984 >>> nsimplify(0.333333333333333, rational=True) 1/3 See Also sympy.core.function.nfloat
"""

from typing import Dict, Any
import sympy as sp
from sympy.simplify.simplify import nsimplify


class SymPyNsimplifyWidget:
    """Widget for SymPy nsimplify function."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the nsimplify function."""
        try:
            # Extract parameters from input
            expr = validated_input.get('expr', None)
            constants = validated_input.get('constants', '()')
            tolerance = validated_input.get('tolerance', 'None')
            full = validated_input.get('full', 'False')
            rational = validated_input.get('rational', 'None')
            rational_conversion = validated_input.get('rational_conversion', 'base10')
            
            # Convert string expressions to SymPy objects where needed
            for key, value in locals().items():
                if key in ['expr', 'constants', 'tolerance', 'full', 'rational', 'rational_conversion'] and isinstance(value, str):
                    try:
                        locals()[key] = sp.sympify(value)
                    except:
                        pass  # Keep as string if sympify fails
            
            # Call the SymPy function
            result = nsimplify(expr, constants, tolerance, full, rational, rational_conversion)
            
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
                    'function': 'nsimplify',
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
                    'function': 'nsimplify',
                    'module': 'sympy.simplify.simplify'
                }
            }
