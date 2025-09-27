"""
SymPy posify Widget
Return ``eq`` (with generic symbols made positive) and a dictionary containing the mapping between the old and new symbols. Explanation Any symbol that has positive=None will be replaced with a positive dummy symbol having the same name. This replacement will allow more symbolic processing of expressions, especially those involving powers and logarithms. A dictionary that can be sent to subs to restore ``eq`` to its original symbols is also returned. >>> from sympy import posify, Symbol, log, solve >>> from sympy.abc import x >>> posify(x + Symbol('p', positive=True) + Symbol('n', negative=True)) (_x + n + p, {_x: x}) >>> eq = 1/x >>> log(eq).expand() log(1/x) >>> log(posify(eq)[0]).expand() -log(_x) >>> p, rep = posify(eq) >>> log(p).expand().subs(rep) -log(x) It is possible to apply the same transformations to an iterable of expressions: >>> eq = x**2 - 4 >>> solve(eq, x) [-2, 2] >>> eq_x, reps = posify([eq, x]); eq_x [_x**2 - 4, _x] >>> solve(*eq_x) [2]
"""


from typing import Dict, Any, Callable
try:
    from ...base_sympy_widget import BaseSymPyWidget
except ImportError:
    try:
        from ..base_sympy_widget import BaseSymPyWidget
    except ImportError:
        from base_sympy_widget import BaseSymPyWidget
from sympy.abc import x


class SymPyPosifyWidget(BaseSymPyWidget):
    """Widget for SymPy x function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return x
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'x',
            'module': 'sympy.abc'
        }
