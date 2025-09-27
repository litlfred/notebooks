"""
SymPy expand_power_base Widget
Wrapper around expand that only uses the power_base hint. A wrapper to expand(power_base=True) which separates a power with a base that is a Mul into a product of powers, without performing any other expansions, provided that assumptions about the power's base and exponent allow. deep=False (default is True) will only apply to the top-level expression. force=True (default is False) will cause the expansion to ignore assumptions about the base and exponent. When False, the expansion will only happen if the base is non-negative or the exponent is an integer. >>> from sympy.abc import x, y, z >>> from sympy import expand_power_base, sin, cos, exp, Symbol >>> (x*y)**2 x**2*y**2 >>> (2*x)**y (2*x)**y >>> expand_power_base(_) 2**y*x**y >>> expand_power_base((x*y)**z) (x*y)**z >>> expand_power_base((x*y)**z, force=True) x**z*y**z >>> expand_power_base(sin((x*y)**z), deep=False) sin((x*y)**z) >>> expand_power_base(sin((x*y)**z), force=True) sin(x**z*y**z) >>> expand_power_base((2*sin(x))**y + (2*cos(x))**y) 2**y*sin(x)**y + 2**y*cos(x)**y >>> expand_power_base((2*exp(y))**x) 2**x*exp(y)**x >>> expand_power_base((2*cos(x))**y) 2**y*cos(x)**y Notice that sums are left untouched. If this is not the desired behavior, apply full ``expand()`` to the expression: >>> expand_power_base(((x+y)*z)**2) z**2*(x + y)**2 >>> (((x+y)*z)**2).expand() x**2*z**2 + 2*x*y*z**2 + y**2*z**2 >>> expand_power_base((2*y)**(1+z)) 2**(z + 1)*y**(z + 1) >>> ((2*y)**(1+z)).expand() 2*2**z*y**(z + 1) The power that is unexpanded can be expanded safely when ``y != 0``, otherwise different values might be obtained for the expression: >>> prev = _ If we indicate that ``y`` is positive but then replace it with a value of 0 after expansion, the expression becomes 0: >>> p = Symbol('p', positive=True) >>> prev.subs(y, p).expand().subs(p, 0) 0 But if ``z = -1`` the expression would not be zero: >>> prev.subs(y, 0).subs(z, -1) 1 See Also expand
"""


from typing import Dict, Any, Callable
try:
    from ...base_sympy_widget import BaseSymPyWidget
except ImportError:
    try:
        from ..base_sympy_widget import BaseSymPyWidget
    except ImportError:
        from base_sympy_widget import BaseSymPyWidget
from sympy.abc import x


class SymPyExpand_Power_BaseWidget(BaseSymPyWidget):
    """Widget for SymPy x function using base class for common functionality."""
    
    def get_sympy_function(self) -> Callable:
        return x
    
    def get_function_info(self) -> Dict[str, str]:
        return {
            'name': 'x',
            'module': 'sympy.abc'
        }
