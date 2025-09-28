"""
SymPy hypersimp Widget
Given combinatorial term f(k) simplify its consecutive term ratio i.e. f(k+1)/f(k).  The input term can be composed of functions and integer sequences which have equivalent representation in terms of gamma special function. Explanation The algorithm performs three basic steps: 1. Rewrite all functions in terms of gamma, if possible. 2. Rewrite all occurrences of gamma in terms of products of gamma and rising factorial with integer,  absolute constant exponent. 3. Perform simplification of nested fractions, powers and if the resulting expression is a quotient of polynomials, reduce their total degree. If f(k) is hypergeometric then as result we arrive with a quotient of polynomials of minimal degree. Otherwise None is returned. For more information on the implemented algorithm refer to: 1. W. Koepf, Algorithms for m-fold Hypergeometric Summation, Journal of Symbolic Computation (1995) 20, 399-417
"""


from typing import Dict, Any, Callable
try:
    from ...base_sympy_widget import BaseSymPyWidget
except ImportError:
    try:
        from ..base_sympy_widget import BaseSymPyWidget
    except ImportError:
        from base_sympy_widget import BaseSymPyWidget
from sympy.simplify.simplify import hypersimp


class SymPyWidgetsSympySimplifySimplifyHypersimpWidget(BaseSymPyWidget):
    """Widget for SymPy hypersimp function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return hypersimp
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'hypersimp',
            'module': 'sympy.simplify.simplify'
        }
