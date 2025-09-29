"""
SymPy nsimplify Widget
Find a simple representation for a number or, if there are free symbols or if ``rational=True``, then replace Floats with their Rational equivalents. If no change is made and rational is not False then Floats will at least be converted to Rationals. Explanation For numerical expressions, a simple formula that numerically matches the given numerical expression is sought (and the input should be possible to evalf to a precision of at least 30 digits). Optionally, a list of (rationally independent) constants to include in the formula may be given. A lower tolerance may be set to find less exact matches. If no tolerance is given then the least precise value will set the tolerance (e.g. Floats default to 15 digits of precision, so would be tolerance=10**-15). With ``full=True``, a more extensive search is performed (this is useful to find simpler numbers when the tolerance is set low). When converting to rational, if rational_conversion='base10' (the default), then convert floats to rationals using their base-10 (string) representation. When rational_conversion='exact' it uses the exact, base-2 representation. Examples >>> from sympy import nsimplify, sqrt, GoldenRatio, exp, I, pi >>> nsimplify(4/(1+sqrt(5)), [GoldenRatio]) -2 + 2*GoldenRatio >>> nsimplify((1/(exp(3*pi*I/5)+1))) 1/2 - I*sqrt(sqrt(5)/10 + 1/4) >>> nsimplify(I**I, [pi]) exp(-pi/2) >>> nsimplify(pi, tolerance=0.01) 22/7 >>> nsimplify(0.333333333333333, rational=True, rational_conversion='exact') 6004799503160655/18014398509481984 >>> nsimplify(0.333333333333333, rational=True) 1/3 See Also sympy.core.function.nfloat
"""


from typing import Dict, Any, Callable
try:
    from ...base_sympy_widget import BaseSymPyWidget
except ImportError:
    try:
        from ..base_sympy_widget import BaseSymPyWidget
    except ImportError:
        from base_sympy_widget import BaseSymPyWidget
from sympy.simplify.simplify import nsimplify


class SymPyWidgetsSympySimplifySimplifyNsimplifyWidget(BaseSymPyWidget):
    """Widget for SymPy nsimplify function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return nsimplify
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'nsimplify',
            'module': 'sympy.simplify.simplify'
        }
