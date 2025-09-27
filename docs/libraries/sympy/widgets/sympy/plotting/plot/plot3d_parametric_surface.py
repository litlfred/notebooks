"""
SymPy plot3d_parametric_surface Widget
Plots a 3D parametric surface plot. Explanation Single plot. ``plot3d_parametric_surface(expr_x, expr_y, expr_z, range_u, range_v, **kwargs)`` If the ranges is not specified, then a default range of (-10, 10) is used. Multiple plots. ``plot3d_parametric_surface((expr_x, expr_y, expr_z, range_u, range_v), ..., **kwargs)`` Ranges have to be specified for every expression. Default range may change in the future if a more advanced default range detection algorithm is implemented. Arguments expr_x : Expression representing the function along ``x``. expr_y : Expression representing the function along ``y``. expr_z : Expression representing the function along ``z``. range_u : (:class:`~.Symbol`, float, float) A 3-tuple denoting the range of the u variable, e.g. (u, 0, 5). range_v : (:class:`~.Symbol`, float, float) A 3-tuple denoting the range of the v variable, e.g. (v, 0, 5). Keyword Arguments Arguments for ``ParametricSurfaceSeries`` class: n1 : int The ``u`` range is sampled uniformly at ``n1`` of points. This keyword argument replaces ``nb_of_points_u``, which should be considered deprecated. n2 : int The ``v`` range is sampled uniformly at ``n2`` of points. This keyword argument replaces ``nb_of_points_v``, which should be considered deprecated. Aesthetics: surface_color : Function which returns a float Specifies the color for the surface of the plot. See :class:`~Plot` for more details. If there are multiple plots, then the same series arguments are applied for all the plots. If you want to set these options separately, you can index the returned ``Plot`` object and set it. Arguments for ``Plot`` class: title : str Title of the plot. size : (float, float), optional A tuple in the form (width, height) in inches to specify the size of the overall figure. The default value is set to ``None``, meaning the size will be set by the default backend. Examples .. plot:: :context: reset :format: doctest :include-source: True >>> from sympy import symbols, cos, sin >>> from sympy.plotting import plot3d_parametric_surface >>> u, v = symbols('u v') Single plot. .. plot:: :context: close-figs :format: doctest :include-source: True >>> plot3d_parametric_surface(cos(u + v), sin(u - v), u - v, ...     (u, -5, 5), (v, -5, 5)) Plot object containing: [0]: parametric cartesian surface: (cos(u + v), sin(u - v), u - v) for u over (-5.0, 5.0) and v over (-5.0, 5.0) See Also Plot, ParametricSurfaceSeries
"""

from typing import Dict, Any
import sympy as sp
from sympy.plotting.plot import plot3d_parametric_surface


class SymPyPlot3D_Parametric_SurfaceWidget:
    """Widget for SymPy plot3d_parametric_surface function."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the plot3d_parametric_surface function."""
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
            result = plot3d_parametric_surface(args, show, kwargs)
            
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
                    'function': 'plot3d_parametric_surface',
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
                    'function': 'plot3d_parametric_surface',
                    'module': 'sympy.plotting.plot'
                }
            }
