"""
SymPy plot3d_parametric_line Widget
Plots a 3D parametric line plot. Usage Single plot: ``plot3d_parametric_line(expr_x, expr_y, expr_z, range, **kwargs)`` If the range is not specified, then a default range of (-10, 10) is used. Multiple plots. ``plot3d_parametric_line((expr_x, expr_y, expr_z, range), ..., **kwargs)`` Ranges have to be specified for every expression. Default range may change in the future if a more advanced default range detection algorithm is implemented. Arguments expr_x : Expression representing the function along x. expr_y : Expression representing the function along y. expr_z : Expression representing the function along z. range : (:class:`~.Symbol`, float, float) A 3-tuple denoting the range of the parameter variable, e.g., (u, 0, 5). Keyword Arguments Arguments for ``Parametric3DLineSeries`` class. n : int The range is uniformly sampled at ``n`` number of points. This keyword argument replaces ``nb_of_points``, which should be considered deprecated. Aesthetics: line_color : string, or float, or function, optional Specifies the color for the plot. See ``Plot`` to see how to set color for the plots. Note that by setting ``line_color``, it would be applied simultaneously to all the series. label : str The label to the plot. It will be used when called with ``legend=True`` to denote the function with the given label in the plot. If there are multiple plots, then the same series arguments are applied to all the plots. If you want to set these options separately, you can index the returned ``Plot`` object and set it. Arguments for ``Plot`` class. title : str Title of the plot. size : (float, float), optional A tuple in the form (width, height) in inches to specify the size of the overall figure. The default value is set to ``None``, meaning the size will be set by the default backend. Examples .. plot:: :context: reset :format: doctest :include-source: True >>> from sympy import symbols, cos, sin >>> from sympy.plotting import plot3d_parametric_line >>> u = symbols('u') Single plot. .. plot:: :context: close-figs :format: doctest :include-source: True >>> plot3d_parametric_line(cos(u), sin(u), u, (u, -5, 5)) Plot object containing: [0]: 3D parametric cartesian line: (cos(u), sin(u), u) for u over (-5.0, 5.0) Multiple plots. .. plot:: :context: close-figs :format: doctest :include-source: True >>> plot3d_parametric_line((cos(u), sin(u), u, (u, -5, 5)), ...     (sin(u), u**2, u, (u, -5, 5))) Plot object containing: [0]: 3D parametric cartesian line: (cos(u), sin(u), u) for u over (-5.0, 5.0) [1]: 3D parametric cartesian line: (sin(u), u**2, u) for u over (-5.0, 5.0) See Also Plot, Parametric3DLineSeries
"""

from typing import Dict, Any
import sympy as sp
from sympy.plotting.plot import plot3d_parametric_line


class SymPyPlot3D_Parametric_LineWidget:
    """Widget for SymPy plot3d_parametric_line function."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def execute(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the plot3d_parametric_line function."""
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
            result = plot3d_parametric_line(args, show, kwargs)
            
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
                    'function': 'plot3d_parametric_line',
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
                    'function': 'plot3d_parametric_line',
                    'module': 'sympy.plotting.plot'
                }
            }
