"""
SymPy separatevars Widget
Separates variables in an expression, if possible.  By default, it separates with respect to all symbols in an expression and collects constant coefficients that are independent of symbols. Explanation If ``dict=True`` then the separated terms will be returned in a dictionary keyed to their corresponding symbols. By default, all symbols in the expression will appear as keys; if symbols are provided, then all those symbols will be used as keys, and any terms in the expression containing other symbols or non-symbols will be returned keyed to the string 'coeff'. (Passing None for symbols will return the expression in a dictionary keyed to 'coeff'.) If ``force=True``, then bases of powers will be separated regardless of assumptions on the symbols involved. Notes The order of the factors is determined by Mul, so that the separated expressions may not necessarily be grouped together. Although factoring is necessary to separate variables in some expressions, it is not necessary in all cases, so one should not count on the returned factors being factored. Examples >>> from sympy.abc import x, y, z, alpha >>> from sympy import separatevars, sin >>> separatevars((x*y)**y) (x*y)**y >>> separatevars((x*y)**y, force=True) x**y*y**y >>> e = 2*x**2*z*sin(y)+2*z*x**2 >>> separatevars(e) 2*x**2*z*(sin(y) + 1) >>> separatevars(e, symbols=(x, y), dict=True) {'coeff': 2*z, x: x**2, y: sin(y) + 1} >>> separatevars(e, [x, y, alpha], dict=True) {'coeff': 2*z, alpha: 1, x: x**2, y: sin(y) + 1} If the expression is not really separable, or is only partially separable, separatevars will do the best it can to separate it by using factoring. >>> separatevars(x + x*y - 3*x**2) -x*(3*x - y - 1) If the expression is not separable then expr is returned unchanged or (if dict=True) then None is returned. >>> eq = 2*x + y*sin(x) >>> separatevars(eq) == eq True >>> separatevars(2*x + y*sin(x), symbols=(x, y), dict=True) is None True
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from typing import Dict, Any, Callable
from base_sympy_widget import BaseSymPyWidget
from sympy.abc import x


class SymPySeparatevarsWidget(BaseSymPyWidget):
    """Widget for SymPy x function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return x
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'x',
            'module': 'sympy.abc'
        }
