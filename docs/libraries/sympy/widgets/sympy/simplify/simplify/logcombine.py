"""
SymPy logcombine Widget
Takes logarithms and combines them using the following rules: - log(x) + log(y) == log(x*y) if both are positive - a*log(x) == log(x**a) if x is positive and a is real If ``force`` is ``True`` then the assumptions above will be assumed to hold if there is no assumption already in place on a quantity. For example, if ``a`` is imaginary or the argument negative, force will not perform a combination but if ``a`` is a symbol with no assumptions the change will take place. Examples >>> from sympy import Symbol, symbols, log, logcombine, I >>> from sympy.abc import a, x, y, z >>> logcombine(a*log(x) + log(y) - log(z)) a*log(x) + log(y) - log(z) >>> logcombine(a*log(x) + log(y) - log(z), force=True) log(x**a*y/z) >>> x,y,z = symbols('x,y,z', positive=True) >>> a = Symbol('a', real=True) >>> logcombine(a*log(x) + log(y) - log(z)) log(x**a*y/z) The transformation is limited to factors and/or terms that contain logs, so the result depends on the initial state of expansion: >>> eq = (2 + 3*I)*log(x) >>> logcombine(eq, force=True) == eq True >>> logcombine(eq.expand(), force=True) log(x**2) + I*log(x**3) See Also posify: replace all symbols with symbols having positive assumptions sympy.core.function.expand_log: expand the logarithms of products and powers; the opposite of logcombine
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from typing import Dict, Any, Callable
from base_sympy_widget import BaseSymPyWidget
from sympy.abc import a


class SymPyLogcombineWidget(BaseSymPyWidget):
    """Widget for SymPy a function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return a
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'a',
            'module': 'sympy.abc'
        }
