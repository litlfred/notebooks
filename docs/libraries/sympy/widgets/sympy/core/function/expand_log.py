"""
SymPy expand_log Widget
Wrapper around expand that only uses the log hint.  See the expand docstring for more information. Examples >>> from sympy import symbols, expand_log, exp, log >>> x, y = symbols('x,y', positive=True) >>> expand_log(exp(x+y)*(x+y)*log(x*y**2)) (x + y)*(log(x) + 2*log(y))*exp(x + y)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from typing import Dict, Any, Callable
from base_sympy_widget import BaseSymPyWidget
from sympy.core.function import expand_log


class SymPyExpand_LogWidget(BaseSymPyWidget):
    """Widget for SymPy expand_log function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return expand_log
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'expand_log',
            'module': 'sympy.core.function'
        }
