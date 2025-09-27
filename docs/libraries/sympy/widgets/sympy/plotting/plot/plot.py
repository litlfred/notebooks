"""
SymPy plot Widget
Plots a function of a single variable as a curve.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from typing import Dict, Any, Callable
from base_sympy_widget import BaseSymPyWidget
from sympy.plotting.plot import plot


class SymPyPlotWidget(BaseSymPyWidget):
    """Widget for SymPy plot function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return plot
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'plot',
            'module': 'sympy.plotting.plot'
        }
