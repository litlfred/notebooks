"""
SymPy lcim Widget
Returns the least common integral multiple of a list of numbers. The numbers can be rational or irrational or a mixture of both. `None` is returned for incommensurable numbers.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from typing import Dict, Any, Callable
from base_sympy_widget import BaseSymPyWidget
from sympy.calculus.util import lcim


class SymPyLcimWidget(BaseSymPyWidget):
    """Widget for SymPy lcim function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return lcim
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'lcim',
            'module': 'sympy.calculus.util'
        }
