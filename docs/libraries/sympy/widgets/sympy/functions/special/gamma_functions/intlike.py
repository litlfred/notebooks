"""
SymPy intlike Widget
SymPy intlike function
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../../'))

from typing import Dict, Any, Callable
from base_sympy_widget import BaseSymPyWidget
from sympy.functions.special.gamma_functions import intlike


class SymPyIntlikeWidget(BaseSymPyWidget):
    """Widget for SymPy intlike function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return intlike
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'intlike',
            'module': 'sympy.functions.special.gamma_functions'
        }
