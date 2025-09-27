"""
SymPy nthroot Widget
Compute a real nth-root of a sum of surds.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from typing import Dict, Any, Callable
from base_sympy_widget import BaseSymPyWidget
from sympy.simplify.simplify import nthroot


class SymPyNthrootWidget(BaseSymPyWidget):
    """Widget for SymPy nthroot function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return nthroot
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'nthroot',
            'module': 'sympy.simplify.simplify'
        }
