"""
SymPy clear_coefficients Widget
Return `p, r` where `p` is the expression obtained when Rational additive and multiplicative coefficients of `expr` have been stripped away in a naive fashion (i.e. without simplification). The operations needed to remove the coefficients will be applied to `rhs` and returned as `r`. Examples >>> from sympy.simplify.simplify import clear_coefficients >>> from sympy.abc import x, y >>> from sympy import Dummy >>> expr = 4*y*(6*x + 3) >>> clear_coefficients(expr - 2) (y*(2*x + 1), 1/6) When solving 2 or more expressions like `expr = a`, `expr = b`, etc..., it is advantageous to provide a Dummy symbol for `rhs` and  simply replace it with `a`, `b`, etc... in `r`. >>> rhs = Dummy('rhs') >>> clear_coefficients(expr, rhs) (y*(2*x + 1), _rhs/12) >>> _[1].subs(rhs, 2) 1/6
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from typing import Dict, Any, Callable
from base_sympy_widget import BaseSymPyWidget
from sympy.simplify.simplify import clear_coefficients


class SymPyClear_CoefficientsWidget(BaseSymPyWidget):
    """Widget for SymPy clear_coefficients function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return clear_coefficients
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'clear_coefficients',
            'module': 'sympy.simplify.simplify'
        }
