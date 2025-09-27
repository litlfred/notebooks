"""
SymPy classof Widget
Get the type of the result when combining matrices of different types. Currently the strategy is that immutability is contagious. Examples >>> from sympy import Matrix, ImmutableMatrix >>> from sympy.matrices.matrixbase import classof >>> M = Matrix([[1, 2], [3, 4]]) # a Mutable Matrix >>> IM = ImmutableMatrix([[1, 2], [3, 4]]) >>> classof(M, IM) <class 'sympy.matrices.immutable.ImmutableDenseMatrix'>
"""


from typing import Dict, Any, Callable
try:
    from ...base_sympy_widget import BaseSymPyWidget
except ImportError:
    try:
        from ..base_sympy_widget import BaseSymPyWidget
    except ImportError:
        from base_sympy_widget import BaseSymPyWidget
from sympy.matrices.matrixbase import classof


class SymPyClassofWidget(BaseSymPyWidget):
    """Widget for SymPy classof function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return classof
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'classof',
            'module': 'sympy.matrices.matrixbase'
        }
