"""
SymPy hypersimilar Widget
Returns True if ``f`` and ``g`` are hyper-similar. Explanation Similarity in hypergeometric sense means that a quotient of f(k) and g(k) is a rational function in ``k``. This procedure is useful in solving recurrence relations. For more information see hypersimp().
"""


from typing import Dict, Any, Callable
try:
    from ...base_sympy_widget import BaseSymPyWidget
except ImportError:
    try:
        from ..base_sympy_widget import BaseSymPyWidget
    except ImportError:
        from base_sympy_widget import BaseSymPyWidget
from sympy.simplify.simplify import hypersimilar


class SymPyHypersimilarWidget(BaseSymPyWidget):
    """Widget for SymPy hypersimilar function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return hypersimilar
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'hypersimilar',
            'module': 'sympy.simplify.simplify'
        }
