"""
from typing import Dict, Any
import sympy as sp
from sympy.simplify.simplify import nc_simplify


class SymPyNc_SimplifyWidget:
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from typing import Dict, Any, Callable
from base_sympy_widget import BaseSymPyWidget
from sympy.simplify.simplify import nc_simplify


class SymPyNc_SimplifyWidget(BaseSymPyWidget):
    """Widget for SymPy nc_simplify function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return nc_simplify
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'nc_simplify',
            'module': 'sympy.simplify.simplify'
        }
