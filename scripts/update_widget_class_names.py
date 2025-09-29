#!/usr/bin/env python3
"""
Update SymPy widget class names to follow hierarchical naming convention.
"""

import os
import glob
import re

def update_widget_class_names():
    """Update all SymPy widget Python files to use hierarchical class names."""
    
    # Mapping of old class names to new hierarchical names
    name_mappings = {
        'SymPyEuler_EquationsWidget': 'SymPyCalculusEulerEulerEquationsWidget',
        'SymPyContinuous_DomainWidget': 'SymPyCalculusUtilContinuousDomainWidget',
        'SymPyFunction_RangeWidget': 'SymPyCalculusUtilFunctionRangeWidget',
        'SymPyIs_ConvexWidget': 'SymPyCalculusUtilIsConvexWidget',
        'SymPyLcimWidget': 'SymPyCalculusUtilLcimWidget',
        'SymPyMaximumWidget': 'SymPyCalculusUtilMaximumWidget',
        'SymPyMinimumWidget': 'SymPyCalculusUtilMinimumWidget',
        'SymPyNot_Empty_InWidget': 'SymPyCalculusUtilNotEmptyInWidget',
        'SymPyPeriodicityWidget': 'SymPyCalculusUtilPeriodicityWidget',
        'SymPyStationary_PointsWidget': 'SymPyCalculusUtilStationaryPointsWidget',
        'SymPyArityWidget': 'SymPyCoreFunctionArityWidget',
        'SymPyCount_OpsWidget': 'SymPyCoreFunctionCountOpsWidget',
        'SymPyDiffWidget': 'SymPyCoreFunctionDiffWidget',
        'SymPyExpandWidget': 'SymPyCoreFunctionExpandWidget',
        'SymPyExpand_ComplexWidget': 'SymPyCoreFunctionExpandComplexWidget',
        'SymPyExpand_FuncWidget': 'SymPyCoreFunctionExpandFuncWidget',
        'SymPyExpand_LogWidget': 'SymPyCoreFunctionExpandLogWidget',
        'SymPyExpand_MulWidget': 'SymPyCoreFunctionExpandMulWidget',
        'SymPyExpand_MultinomialWidget': 'SymPyCoreFunctionExpandMultinomialWidget',
        'SymPyExpand_Power_BaseWidget': 'SymPyCoreFunctionExpandPowerBaseWidget',
        'SymPyExpand_Power_ExpWidget': 'SymPyCoreFunctionExpandPowerExpWidget',
        'SymPyExpand_TrigWidget': 'SymPyCoreFunctionExpandTrigWidget',
        'SymPyNfloatWidget': 'SymPyCoreFunctionNfloatWidget',
        'SymPyMatch_Real_ImagWidget': 'SymPyFunctionsElementaryExponentialMatchRealImagWidget',
        'SymPyCbrtWidget': 'SymPyFunctionsElementaryMiscellaneousCbrtWidget',
        'SymPyReal_RootWidget': 'SymPyFunctionsElementaryMiscellaneousRealRootWidget',
        'SymPyRootWidget': 'SymPyFunctionsElementaryMiscellaneousRootWidget',
        'SymPySqrtWidget': 'SymPyFunctionsElementaryMiscellaneousSqrtWidget',
        'SymPySimplifyWidget': 'SymPySimplifySimplifySimplifyWidget'
    }
    
    # Find all SymPy widget files
    widget_files = glob.glob('/home/runner/work/notebooks/notebooks/docs/libraries/sympy/widgets/sympy/**/*.py', recursive=True)
    
    updated_files = []
    
    for file_path in widget_files:
        if 'base_sympy_widget.py' in file_path:
            continue
            
        # Read file content
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Track if any changes were made
        original_content = content
        
        # Update class names
        for old_name, new_name in name_mappings.items():
            if old_name in content:
                content = content.replace(old_name, new_name)
                print(f"Updated {old_name} -> {new_name} in {file_path}")
        
        # Also update generic patterns
        # Find class definitions like "class SymPyXxxWidget"
        class_pattern = r'class (SymPy\w+Widget)\(BaseSymPyWidget\):'
        matches = re.findall(class_pattern, content)
        
        for old_class_name in matches:
            if old_class_name not in name_mappings:
                # Try to generate a hierarchical name based on file path
                path_parts = file_path.split('/')
                if 'sympy' in path_parts:
                    sympy_index = path_parts.index('sympy')
                    module_parts = path_parts[sympy_index+1:-1]  # Exclude file name
                    file_name = path_parts[-1].replace('.py', '')
                    
                    # Create hierarchical name
                    all_parts = ['SymPy'] + [part.replace('_', '').title() for part in module_parts] + [file_name.replace('_', '').title()]
                    new_class_name = ''.join(all_parts) + 'Widget'
                    
                    if new_class_name != old_class_name:
                        content = content.replace(old_class_name, new_class_name)
                        print(f"Generated hierarchical name: {old_class_name} -> {new_class_name} in {file_path}")
        
        # Write back if changed
        if content != original_content:
            with open(file_path, 'w') as f:
                f.write(content)
            updated_files.append(file_path)
    
    return updated_files

if __name__ == "__main__":
    updated_files = update_widget_class_names()
    print(f"\nUpdated {len(updated_files)} widget files with hierarchical class names.")