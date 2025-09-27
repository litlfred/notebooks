"""
SymPy product_simplify Widget
Main function for Product simplification
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from typing import Dict, Any, Callable
from base_sympy_widget import BaseSymPyWidget
from sympy.simplify.simplify import product_simplify


class SymPyProduct_SimplifyWidget(BaseSymPyWidget):
    """Widget for SymPy product_simplify function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return product_simplify
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'product_simplify',
            'module': 'sympy.simplify.simplify'
        }
