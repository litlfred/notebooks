#!/usr/bin/env python3
"""
Test script to verify the notebook fixes work correctly.
"""

import json

def test_notebook_structure():
    """Test that the notebook has the correct structure to avoid NameError."""
    
    with open('legacy/weierstrass_playground.ipynb', 'r') as f:
        nb = json.load(f)
    
    # Extract code cells
    code_cells = []
    for cell in nb['cells']:
        if cell['cell_type'] == 'code':
            code = ''.join(cell['source'])
            code_cells.append(code)
    
    print(f"Found {len(code_cells)} code cells")
    
    # Check if the problematic UI cell now has safety checks
    ui_cell_found = False
    for i, code in enumerate(code_cells):
        if 'lattice_box = widgets.VBox' in code:
            ui_cell_found = True
            print(f"Found UI layout cell (cell {i+1})")
            
            # Check if it has the safety check
            if 'try:' in code and 'p_slider' in code and 'except NameError:' in code:
                print("✓ UI cell has safety check for undefined variables")
                return True
            else:
                print("✗ UI cell missing safety check")
                return False
    
    if not ui_cell_found:
        print("✗ UI layout cell not found")
        return False
    
    return True

def test_notebook_instructions():
    """Test that the notebook has proper usage instructions."""
    
    with open('legacy/weierstrass_playground.ipynb', 'r') as f:
        nb = json.load(f)
    
    # Check first markdown cell for instructions
    first_markdown = None
    for cell in nb['cells']:
        if cell['cell_type'] == 'markdown':
            first_markdown = ''.join(cell['source'])
            break
    
    if first_markdown and 'Important: How to Use This Notebook' in first_markdown:
        print("✓ Notebook has usage instructions")
        return True
    else:
        print("✗ Notebook missing usage instructions")
        return False

def main():
    """Run all tests."""
    print("Testing notebook fixes...")
    
    tests_passed = 0
    total_tests = 2
    
    if test_notebook_structure():
        tests_passed += 1
    
    if test_notebook_instructions():
        tests_passed += 1
    
    print(f"\nTest Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! The NameError issue should be fixed.")
        return True
    else:
        print("⚠️ Some tests failed.")
        return False

if __name__ == "__main__":
    main()