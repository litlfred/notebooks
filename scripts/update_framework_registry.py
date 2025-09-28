#!/usr/bin/env python3
"""
Script to update the new widget framework registry with SymPy widget class associations.
"""

import os
import json

def generate_sympy_class_mappings():
    """Generate JSON-LD class name to ID mappings for all SymPy widgets."""
    
    # Base mappings from the current framework
    base_mappings = {
        'WidgetExecutor': 'base-widget',
        'StickyNoteWidget': 'sticky-note',
        'PythonCodeWidget': 'python-code', 
        'DataVisualizationWidget': 'data-visualization',
        'ArrowWidget': 'arrow',
        'PQTorusWidget': 'pq-torus',
        'PQTorusWeierstrassTwoPanelWidget': 'pq-torus.weierstrass.two-panel',
        'PQTorusWeierstrassThreePanelWidget': 'pq-torus.weierstrass.three-panel',
        'PQTorusWeierstrassFivePanelWidget': 'pq-torus.weierstrass.five-panel',
        'PQTorusWeierstrassTrajectoriesWidget': 'pq-torus.weierstrass.trajectories',
        'PQTorusWeierstrassContoursWidget': 'pq-torus.weierstrass.contours'
    }
    
    # SymPy widget mappings based on the hierarchical naming convention
    sympy_modules = [
        'calculus.euler.euler_equations',
        'calculus.util.continuous_domain',
        'calculus.util.function_range',
        'calculus.util.is_convex',
        'calculus.util.lcim',
        'calculus.util.maximum',
        'calculus.util.minimum',
        'calculus.util.not_empty_in',
        'calculus.util.periodicity',
        'calculus.util.stationary_points',
        'core.function.arity',
        'core.function.count_ops',
        'core.function.diff',
        'core.function.expand',
        'core.function.expand_complex',
        'core.function.expand_func',
        'core.function.expand_log',
        'core.function.expand_mul',
        'core.function.expand_multinomial',
        'core.function.expand_power_base',
        'core.function.expand_power_exp',
        'core.function.expand_trig',
        'core.function.nfloat',
        'functions.elementary.exponential.match_real_imag',
        'functions.elementary.miscellaneous.cbrt',
        'functions.elementary.miscellaneous.real_root',
        'functions.elementary.miscellaneous.root',
        'functions.elementary.miscellaneous.sqrt',
        'functions.special.bessel.assume_integer_order',
        'functions.special.bessel.jn_zeros',
        'functions.special.gamma_functions.intlike',
        'geometry.polygon.deg',
        'geometry.polygon.rad',
        'matrices.common.a2idx',
        'matrices.common.classof',
        'plotting.plot.check_arguments',
        'plotting.plot.plot',
        'plotting.plot.plot3d',
        'plotting.plot.plot3d_parametric_line',
        'plotting.plot.plot3d_parametric_surface',
        'plotting.plot.plot_contour',
        'plotting.plot.plot_factory',
        'plotting.plot.plot_parametric',
        'simplify.simplify.besselsimp',
        'simplify.simplify.clear_coefficients',
        'simplify.simplify.dotprodsimp',
        'simplify.simplify.factor_sum',
        'simplify.simplify.hypersimilar',
        'simplify.simplify.hypersimp',
        'simplify.simplify.inversecombine',
        'simplify.simplify.kroneckersimp',
        'simplify.simplify.logcombine',
        'simplify.simplify.nc_simplify',
        'simplify.simplify.nsimplify',
        'simplify.simplify.nthroot',
        'simplify.simplify.posify',
        'simplify.simplify.product_mul',
        'simplify.simplify.product_simplify',
        'simplify.simplify.separatevars',
        'simplify.simplify.signsimp',
        'simplify.simplify.simplify',
        'simplify.simplify.sum_add',
        'simplify.simplify.sum_combine',
        'simplify.simplify.sum_simplify'
    ]
    
    # Generate class name mappings for SymPy widgets
    sympy_mappings = {}
    for module_path in sympy_modules:
        # Convert module path to class name (hierarchical naming)
        class_parts = ['SymPy'] + [part.replace('_', '').title() for part in module_path.split('.')]
        class_name = ''.join(class_parts) + 'Widget'
        
        # Create JSON-LD ID
        jsonld_id = f"sympy.{module_path.replace('_', '-')}"
        
        sympy_mappings[class_name] = jsonld_id
    
    # Combine all mappings
    all_mappings = {**base_mappings, **sympy_mappings}
    
    return all_mappings

if __name__ == "__main__":
    mappings = generate_sympy_class_mappings()
    print(f"Generated {len(mappings)} class mappings for SymPy widgets:")
    sympy_mappings = {k: v for k, v in mappings.items() if k.startswith('SymPy')}
    print(f"SymPy-specific mappings: {len(sympy_mappings)}")
    
    # Print first few examples
    for i, (class_name, jsonld_id) in enumerate(sympy_mappings.items()):
        if i < 5:
            print(f"  {class_name} -> {jsonld_id}")
    print("  ...")