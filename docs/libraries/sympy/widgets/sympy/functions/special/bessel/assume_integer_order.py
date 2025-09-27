"""
SymPy assume_integer_order Widget
SymPy assume_integer_order function
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../../'))

from typing import Dict, Any, Callable
from base_sympy_widget import BaseSymPyWidget
from sympy.functions.special.bessel import assume_integer_order


class SymPyAssume_Integer_OrderWidget(BaseSymPyWidget):
    """Widget for SymPy assume_integer_order function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return assume_integer_order
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'assume_integer_order',
            'module': 'sympy.functions.special.bessel'
        }
