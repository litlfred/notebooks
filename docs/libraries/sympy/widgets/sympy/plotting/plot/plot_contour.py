"""
SymPy plot_contour Widget
Draws contour plot of a function Usage Single plot ``plot_contour(expr, range_x, range_y, **kwargs)`` If the ranges are not specified, then a default range of (-10, 10) is used. Multiple plot with the same range. ``plot_contour(expr1, expr2, range_x, range_y, **kwargs)`` If the ranges are not specified, then a default range of (-10, 10) is used. Multiple plots with different ranges. ``plot_contour((expr1, range_x, range_y), (expr2, range_x, range_y), ..., **kwargs)`` Ranges have to be specified for every expression. Default range may change in the future if a more advanced default range detection algorithm is implemented. Arguments expr : Expression representing the function along x. range_x : (:class:`Symbol`, float, float) A 3-tuple denoting the range of the x variable, e.g. (x, 0, 5). range_y : (:class:`Symbol`, float, float) A 3-tuple denoting the range of the y variable, e.g. (y, 0, 5). Keyword Arguments Arguments for ``ContourSeries`` class: n1 : int The x range is sampled uniformly at ``n1`` of points. This keyword argument replaces ``nb_of_points_x``, which should be considered deprecated. n2 : int The y range is sampled uniformly at ``n2`` of points. This keyword argument replaces ``nb_of_points_y``, which should be considered deprecated. Aesthetics: surface_color : Function which returns a float Specifies the color for the surface of the plot. See :class:`sympy.plotting.Plot` for more details. If there are multiple plots, then the same series arguments are applied to all the plots. If you want to set these options separately, you can index the returned ``Plot`` object and set it. Arguments for ``Plot`` class: title : str Title of the plot. size : (float, float), optional A tuple in the form (width, height) in inches to specify the size of the overall figure. The default value is set to ``None``, meaning the size will be set by the default backend. See Also Plot, ContourSeries
"""


from typing import Dict, Any, Callable
try:
    from ...base_sympy_widget import BaseSymPyWidget
except ImportError:
    try:
        from ..base_sympy_widget import BaseSymPyWidget
    except ImportError:
        from base_sympy_widget import BaseSymPyWidget
from sympy.plotting.plot import plot_contour


class SymPyPlot_ContourWidget(BaseSymPyWidget):
    """Widget for SymPy plot_contour function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return plot_contour
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'plot_contour',
            'module': 'sympy.plotting.plot'
        }
