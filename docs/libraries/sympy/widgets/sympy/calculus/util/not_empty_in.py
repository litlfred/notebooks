"""
SymPy not_empty_in Widget
Finds the domain of the functions in ``finset_intersection`` in which the ``finite_set`` is not-empty.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from typing import Dict, Any, Callable
from base_sympy_widget import BaseSymPyWidget
from sympy.calculus.util import not_empty_in


class SymPyNot_Empty_InWidget(BaseSymPyWidget):
    """Widget for SymPy not_empty_in function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return not_empty_in
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'not_empty_in',
            'module': 'sympy.calculus.util'
        }
