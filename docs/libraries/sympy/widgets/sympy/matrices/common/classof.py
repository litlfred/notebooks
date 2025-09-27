"""
SymPy classof Widget
Get the type of the result when combining matrices of different types. Currently the strategy is that immutability is contagious. Examples >>> from sympy import Matrix, ImmutableMatrix >>> from sympy.matrices.matrixbase import classof >>> M = Matrix([[1, 2], [3, 4]]) # a Mutable Matrix >>> IM = ImmutableMatrix([[1, 2], [3, 4]]) >>> classof(M, IM) <class 'sympy.matrices.immutable.ImmutableDenseMatrix'>
"""

from typing import Dict, Any
import sympy as sp
from sympy.matrices.common import classof


class SymPyClassofWidget:
    """Widget for SymPy classof function."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the classof function."""
        try:
            # Extract parameters from input
            A = validated_input.get('A', None)
            B = validated_input.get('B', None)
            
            # Convert string expressions to SymPy objects where needed
            for key, value in locals().items():
                if key in ['A', 'B'] and isinstance(value, str):
                    try:
                        locals()[key] = sp.sympify(value)
                    except:
                        pass  # Keep as string if sympify fails
            
            # Call the SymPy function
            result = classof(A, B)
            
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
                    'function': 'classof',
                    'module': 'sympy.matrices.common',
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
                    'function': 'classof',
                    'module': 'sympy.matrices.common'
                }
            }
