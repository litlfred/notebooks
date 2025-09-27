"""
SymPy arity Widget
Return the arity of the function if it is known, else None. Explanation When default values are specified for some arguments, they are optional and the arity is reported as a tuple of possible values. Examples >>> from sympy import arity, log >>> arity(lambda x: x) 1 >>> arity(log) (1, 2) >>> arity(lambda *x: sum(x)) is None True
"""

from typing import Dict, Any
import sympy as sp
from sympy.core.function import arity


class SymPyArityWidget:
    """Widget for SymPy arity function."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the arity function."""
        try:
            # Extract parameters from input
            cls = validated_input.get('cls', None)
            
            # Convert string expressions to SymPy objects where needed
            for key, value in locals().items():
                if key in ['cls'] and isinstance(value, str):
                    try:
                        locals()[key] = sp.sympify(value)
                    except:
                        pass  # Keep as string if sympify fails
            
            # Call the SymPy function
            result = arity(cls)
            
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
                    'function': 'arity',
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
                    'function': 'arity',
                    'module': 'sympy.core.function'
                }
            }
