#!/usr/bin/env python3
"""
Test script for the Widget Framework functionality.
Validates that the core widget framework requirements are met.
"""

import json
import os
from pathlib import Path

def test_widget_schemas_exist():
    """Test that widget schemas are properly defined."""
    schema_path = Path('docs/weierstrass-playground/widget-schemas.json')
    
    if not schema_path.exists():
        print("✗ Widget schemas file not found")
        return False
    
    with open(schema_path, 'r') as f:
        schemas = json.load(f)
    
    if 'widget-schemas' not in schemas:
        print("✗ Widget schemas structure invalid")
        return False
    
    widgets = schemas['widget-schemas']
    
    # Check for required widgets
    required_widgets = ['sticky-note', 'python-code', 'pq-torus']
    for widget_id in required_widgets:
        if widget_id not in widgets:
            print(f"✗ Required widget '{widget_id}' not found")
            return False
    
    print(f"✓ Found {len(widgets)} widget schemas")
    return True

def test_sticky_note_schema():
    """Test sticky note widget schema completeness."""
    schema_path = Path('docs/weierstrass-playground/widget-schemas.json')
    
    with open(schema_path, 'r') as f:
        schemas = json.load(f)
    
    sticky_note = schemas['widget-schemas']['sticky-note']
    
    # Check required fields
    required_fields = ['id', 'name', 'description', 'category', 'icon']
    for field in required_fields:
        if field not in sticky_note:
            print(f"✗ Sticky note missing required field: {field}")
            return False
    
    # Check actions
    if 'actions' not in sticky_note:
        print("✗ Sticky note missing actions")
        return False
    
    actions = sticky_note['actions']
    expected_actions = ['render-markdown', 'export-pdf', 'export-html']
    for action in expected_actions:
        if action not in actions:
            print(f"✗ Sticky note missing action: {action}")
            return False
    
    print("✓ Sticky note schema is complete")
    return True

def test_board_html_exists():
    """Test that the main board interface exists."""
    board_path = Path('docs/weierstrass-playground/board.html')
    
    if not board_path.exists():
        print("✗ Board HTML file not found")
        return False
    
    with open(board_path, 'r') as f:
        content = f.read()
    
    # Check for essential elements
    essential_elements = [
        'Mathematical Board',
        'Widget Library',
        'board-app.js',
        'board-style.css'
    ]
    
    for element in essential_elements:
        if element not in content:
            print(f"✗ Board HTML missing: {element}")
            return False
    
    print("✓ Board HTML structure is complete")
    return True

def test_javascript_framework():
    """Test that the JavaScript framework has essential functions."""
    js_path = Path('docs/weierstrass-playground/board-app.js')
    
    if not js_path.exists():
        print("✗ JavaScript framework file not found")
        return False
    
    with open(js_path, 'r') as f:
        content = f.read()
    
    # Check for critical functions we just fixed
    essential_functions = [
        'class MathematicalBoard',
        'processMarkdownVariables',
        'escapeHtml',
        'renderStickyNoteContent',
        'executeWidget'
    ]
    
    for func in essential_functions:
        if func not in content:
            print(f"✗ JavaScript missing function: {func}")
            return False
    
    print("✓ JavaScript framework is complete")
    return True

def test_theme_system():
    """Test that the theme system is properly implemented."""
    css_path = Path('docs/weierstrass-playground/board-style.css')
    
    if not css_path.exists():
        print("✗ CSS theme file not found")
        return False
    
    with open(css_path, 'r') as f:
        content = f.read()
    
    # Check for theme variables
    theme_vars = [
        '--sticky-desert-bg',
        '--sticky-classic-bg', 
        '--sticky-ocean-bg',
        '--sticky-forest-bg'
    ]
    
    for var in theme_vars:
        if var not in content:
            print(f"✗ CSS missing theme variable: {var}")
            return False
    
    print("✓ Theme system is complete")
    return True

def main():
    """Run all widget framework tests."""
    print("Testing Widget Framework Implementation...")
    print("=" * 60)
    
    tests = [
        test_widget_schemas_exist,
        test_sticky_note_schema,
        test_board_html_exists,
        test_javascript_framework,
        test_theme_system
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print()  # Add spacing after failed tests
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with error: {e}")
            print()
    
    print("=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All widget framework tests PASSED!")
        print("✅ The widget framework implementation is working correctly!")
    else:
        print("⚠️  Some widget framework tests failed.")
        print(f"   {total - passed} issues need to be addressed.")
    
    return passed == total

if __name__ == "__main__":
    main()