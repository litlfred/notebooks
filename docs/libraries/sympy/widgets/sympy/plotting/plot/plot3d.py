"""
SymPy plot3d Widget
Plots a 3D surface plot. Usage Single plot ``plot3d(expr, range_x, range_y, **kwargs)`` If the ranges are not specified, then a default range of (-10, 10) is used. Multiple plot with the same range. ``plot3d(expr1, expr2, range_x, range_y, **kwargs)`` If the ranges are not specified, then a default range of (-10, 10) is used. Multiple plots with different ranges. ``plot3d((expr1, range_x, range_y), (expr2, range_x, range_y), ..., **kwargs)`` Ranges have to be specified for every expression. Default range may change in the future if a more advanced default range detection algorithm is implemented. Arguments expr : Expression representing the function along x. range_x : (:class:`~.Symbol`, float, float) A 3-tuple denoting the range of the x variable, e.g. (x, 0, 5). range_y : (:class:`~.Symbol`, float, float) A 3-tuple denoting the range of the y variable, e.g. (y, 0, 5). Keyword Arguments Arguments for ``SurfaceOver2DRangeSeries`` class: n1 : int The x range is sampled uniformly at ``n1`` of points. This keyword argument replaces ``nb_of_points_x``, which should be considered deprecated. n2 : int The y range is sampled uniformly at ``n2`` of points. This keyword argument replaces ``nb_of_points_y``, which should be considered deprecated. Aesthetics: surface_color : Function which returns a float Specifies the color for the surface of the plot. See :class:`~.Plot` for more details. If there are multiple plots, then the same series arguments are applied to all the plots. If you want to set these options separately, you can index the returned ``Plot`` object and set it. Arguments for ``Plot`` class: title : str Title of the plot. size : (float, float), optional A tuple in the form (width, height) in inches to specify the size of the overall figure. The default value is set to ``None``, meaning the size will be set by the default backend. Examples .. plot:: :context: reset :format: doctest :include-source: True >>> from sympy import symbols >>> from sympy.plotting import plot3d >>> x, y = symbols('x y') Single plot .. plot:: :context: close-figs :format: doctest :include-source: True >>> plot3d(x*y, (x, -5, 5), (y, -5, 5)) Plot object containing: [0]: cartesian surface: x*y for x over (-5.0, 5.0) and y over (-5.0, 5.0) Multiple plots with same range .. plot:: :context: close-figs :format: doctest :include-source: True >>> plot3d(x*y, -x*y, (x, -5, 5), (y, -5, 5)) Plot object containing: [0]: cartesian surface: x*y for x over (-5.0, 5.0) and y over (-5.0, 5.0) [1]: cartesian surface: -x*y for x over (-5.0, 5.0) and y over (-5.0, 5.0) Multiple plots with different ranges. .. plot:: :context: close-figs :format: doctest :include-source: True >>> plot3d((x**2 + y**2, (x, -5, 5), (y, -5, 5)), ...     (x*y, (x, -3, 3), (y, -3, 3))) Plot object containing: [0]: cartesian surface: x**2 + y**2 for x over (-5.0, 5.0) and y over (-5.0, 5.0) [1]: cartesian surface: x*y for x over (-3.0, 3.0) and y over (-3.0, 3.0) See Also Plot, SurfaceOver2DRangeSeries
"""

from typing import Dict, Any
import sympy as sp
from sympy.plotting.plot import plot3d


class SymPyPlot3DWidget:
    """Widget for SymPy plot3d function."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the plot3d function."""
        try:
            # Extract parameters from input
            args = validated_input.get('args', None)
            show = validated_input.get('show', 'True')
            kwargs = validated_input.get('kwargs', None)
            
            # Convert string expressions to SymPy objects where needed
            for key, value in locals().items():
                if key in ['args', 'show', 'kwargs'] and isinstance(value, str):
                    try:
                        locals()[key] = sp.sympify(value)
                    except:
                        pass  # Keep as string if sympify fails
            
            # Call the SymPy function
            result = plot3d(args, show, kwargs)
            
            # Format output
            result_str = str(result)
            try:
                latex_str = sp.latex(result) if hasattr(result, '_latex') or hasattr(sp, 'latex') else result_str
            except:
                latex_str = result_str
            
            return {
                'result': result_str,
                'latex': latex_str,
                'metadata': {
                    'function': 'plot3d',
                    'module': 'sympy.plotting.plot',
                    'result_type': type(result).__name__,
                    'parameters_used': validated_input
                }
            }
            
        except Exception as e:
            return {
                'result': f"Error: {str(e)}",
                'latex': "\\text{Error}",
                'metadata': {
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'function': 'plot3d',
                    'module': 'sympy.plotting.plot'
                }
            }
