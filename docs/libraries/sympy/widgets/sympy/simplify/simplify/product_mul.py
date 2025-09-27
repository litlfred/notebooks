"""
SymPy product_mul Widget
Helper function for Product simplification
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from typing import Dict, Any, Callable
from base_sympy_widget import BaseSymPyWidget
from sympy.simplify.simplify import product_mul


class SymPyProduct_MulWidget(BaseSymPyWidget):
    """Widget for SymPy product_mul function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return product_mul
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'product_mul',
            'module': 'sympy.simplify.simplify'
        }
