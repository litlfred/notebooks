"""
SymPy Matrices Dense Widget
Widget for SymPy dense matrix operations
"""

from typing import Dict, Any
import sympy as sp
import json


class SymPyMatricesDenseWidget:
    """Widget for SymPy dense matrix operations."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute matrix operations."""
        try:
            # Parse matrix expression or create default matrix
            expression_str = validated_input.get('expression', '[[1, 2], [3, 4]]')
            
            # Try to parse as matrix
            if expression_str.startswith('[[') and expression_str.endswith(']]'):
                # Parse as nested list
                matrix_data = json.loads(expression_str)
                matrix = sp.Matrix(matrix_data)
            else:
                # Try to parse as SymPy expression
                matrix = sp.sympify(expression_str)
                if not isinstance(matrix, sp.Matrix):
                    # Create a 2x2 matrix from the expression
                    matrix = sp.Matrix([[expression_str, 0], [0, expression_str]])
            
            # Perform various matrix operations
            operations = {}
            
            try:
                operations['original'] = str(matrix)
                operations['shape'] = f"{matrix.rows}x{matrix.cols}"
                operations['determinant'] = str(matrix.det()) if matrix.is_square else "N/A (not square)"
                operations['transpose'] = str(matrix.T)
                
                if matrix.is_square and matrix.rows <= 4:  # Avoid expensive operations on large matrices
                    try:
                        operations['eigenvalues'] = str(matrix.eigenvals())
                    except:
                        operations['eigenvalues'] = "Could not compute"
                        
                    try:
                        operations['inverse'] = str(matrix.inv()) if matrix.det() != 0 else "Not invertible"
                    except:
                        operations['inverse'] = "Could not compute inverse"
            except Exception as e:
                operations['error'] = str(e)
            
            result_parts = []
            for op_name, op_result in operations.items():
                result_parts.append(f"{op_name}: {op_result}")
            
            result = "\n".join(result_parts)
            latex = sp.latex(matrix)
            
            return {
                'result': result,
                'latex': latex,
                'metadata': {
                    'matrix_shape': f"{matrix.rows}x{matrix.cols}",
                    'is_square': matrix.is_square,
                    'operations_performed': list(operations.keys())
                }
            }
            
        except Exception as e:
            return {
                'result': f"Error: {str(e)}",
                'latex': "\\text{Error}",
                'metadata': {
                    'error': str(e),
                    'error_type': type(e).__name__
                }
            }