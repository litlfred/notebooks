"""
SymPy jn_zeros Widget
Zeros of the spherical Bessel function of the first kind. Explanation This returns an array of zeros of $jn$ up to the $k$-th zero. * method = "sympy": uses `mpmath.besseljzero <https://mpmath.org/doc/current/functions/bessel.html#mpmath.besseljzero>`_ * method = "scipy": uses the `SciPy's sph_jn <https://docs.scipy.org/doc/scipy/reference/generated/scipy.special.jn_zeros.html>`_ and `newton <https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.newton.html>`_ to find all roots, which is faster than computing the zeros using a general numerical solver, but it requires SciPy and only works with low precision floating point numbers. (The function used with method="sympy" is a recent addition to mpmath; before that a general solver was used.) Examples >>> from sympy import jn_zeros >>> jn_zeros(2, 4, dps=5) [5.7635, 9.095, 12.323, 15.515] See Also jn, yn, besselj, besselk, bessely
"""

from typing import Dict, Any
import sympy as sp
from sympy.functions.special.bessel import jn_zeros


class SymPyJn_ZerosWidget:
    """Widget for SymPy jn_zeros function."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the jn_zeros function."""
        try:
            # Extract parameters from input
            n = validated_input.get('n', None)
            k = validated_input.get('k', None)
            method = validated_input.get('method', 'sympy')
            dps = validated_input.get('dps', '15')
            
            # Convert string expressions to SymPy objects where needed
            for key, value in locals().items():
                if key in ['n', 'k', 'method', 'dps'] and isinstance(value, str):
                    try:
                        locals()[key] = sp.sympify(value)
                    except:
                        pass  # Keep as string if sympify fails
            
            # Call the SymPy function
            result = jn_zeros(n, k, method, dps)
            
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
                    'function': 'jn_zeros',
                    'module': 'sympy.functions.special.bessel',
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
                    'function': 'jn_zeros',
                    'module': 'sympy.functions.special.bessel'
                }
            }
