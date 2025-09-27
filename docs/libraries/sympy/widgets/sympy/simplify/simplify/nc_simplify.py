"""
SymPy nc_simplify Widget
Simplify a non-commutative expression composed of multiplication and raising to a power by grouping repeated subterms into one power. Priority is given to simplifications that give the fewest number of arguments in the end (for example, in a*b*a*b*c*a*b*c simplifying to (a*b)**2*c*a*b*c gives 5 arguments while a*b*(a*b*c)**2 has 3). If ``expr`` is a sum of such terms, the sum of the simplified terms is returned. Keyword argument ``deep`` controls whether or not subexpressions nested deeper inside the main expression are simplified. See examples below. Setting `deep` to `False` can save time on nested expressions that do not need simplifying on all levels. Examples >>> from sympy import symbols >>> from sympy.simplify.simplify import nc_simplify >>> a, b, c = symbols("a b c", commutative=False) >>> nc_simplify(a*b*a*b*c*a*b*c) a*b*(a*b*c)**2 >>> expr = a**2*b*a**4*b*a**4 >>> nc_simplify(expr) a**2*(b*a**4)**2 >>> nc_simplify(a*b*a*b*c**2*(a*b)**2*c**2) ((a*b)**2*c**2)**2 >>> nc_simplify(a*b*a*b + 2*a*c*a**2*c*a**2*c*a) (a*b)**2 + 2*(a*c*a)**3 >>> nc_simplify(b**-1*a**-1*(a*b)**2) a*b >>> nc_simplify(a**-1*b**-1*c*a) (b*a)**(-1)*c*a >>> expr = (a*b*a*b)**2*a*c*a*c >>> nc_simplify(expr) (a*b)**4*(a*c)**2 >>> nc_simplify(expr, deep=False) (a*b*a*b)**2*(a*c)**2
"""

from typing import Dict, Any
import sympy as sp
from sympy.simplify.simplify import nc_simplify


class SymPyNc_SimplifyWidget:
    """Widget for SymPy nc_simplify function."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the nc_simplify function."""
        try:
            # Extract parameters from input
            expr = validated_input.get('expr', None)
            deep = validated_input.get('deep', 'True')
            
            # Convert string expressions to SymPy objects where needed
            for key, value in locals().items():
                if key in ['expr', 'deep'] and isinstance(value, str):
                    try:
                        locals()[key] = sp.sympify(value)
                    except:
                        pass  # Keep as string if sympify fails
            
            # Call the SymPy function
            result = nc_simplify(expr, deep)
            
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
                    'function': 'nc_simplify',
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
                    'function': 'nc_simplify',
                    'module': 'sympy.simplify.simplify'
                }
            }
