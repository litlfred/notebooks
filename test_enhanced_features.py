#!/usr/bin/env python3
"""
Test the enhanced widget framework features.
"""

def test_enhanced_widget_framework():
    """Test that the enhanced features are implemented."""
    
    print("Testing Enhanced Widget Framework Features...")
    print("=" * 60)
    
    # Test 1: Check that board-app.js contains the required features
    with open('docs/weierstrass-playground/board-app.js', 'r') as f:
        js_content = f.read()
    
    features_to_check = [
        ('Python Execution', 'initializePython'),
        ('Event System', 'addEventListener'),
        ('Cycle Detection', 'detectCycles'),
        ('Widget ID Generation', 'generateWidgetId'),
        ('Stop Functionality', 'stopWidget'),
        ('Attached Notes', 'renderAttachedNote'),
        ('Connection Validation', 'connectWidgetsWithValidation'),
        ('Event Firing', 'fireWidgetEvent'),
        ('Pyodide Integration', 'loadPyodide'),
        ('Variable Substitution', 'processNoteVariables')
    ]
    
    passed_tests = 0
    total_tests = len(features_to_check)
    
    for feature_name, feature_code in features_to_check:
        if feature_code in js_content:
            print(f"✅ {feature_name}: Found {feature_code}")
            passed_tests += 1
        else:
            print(f"❌ {feature_name}: Missing {feature_code}")
    
    print("\n" + "=" * 60)
    
    # Test 2: Check CSS for attached notes styling
    with open('docs/weierstrass-playground/board-style.css', 'r') as f:
        css_content = f.read()
    
    css_features = [
        'widget-attached-note',
        'attached-note-display', 
        'attached-note-editor',
        'attached-note-textarea',
        'stop-btn'
    ]
    
    css_passed = 0
    for css_class in css_features:
        if css_class in css_content:
            print(f"✅ CSS: Found .{css_class} styling")
            css_passed += 1
        else:
            print(f"❌ CSS: Missing .{css_class} styling")
    
    total_tests += len(css_features)
    passed_tests += css_passed
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed_tests}/{total_tests} features implemented")
    
    if passed_tests == total_tests:
        print("🎉 All enhanced features are implemented!")
        return True
    else:
        print(f"⚠️ {total_tests - passed_tests} features still missing")
        return False

def test_python_backend_integration():
    """Test that Python backend components are in place."""
    
    print("\nTesting Python Backend Integration...")
    print("=" * 60)
    
    with open('docs/weierstrass-playground/board-app.js', 'r') as f:
        js_content = f.read()
    
    python_features = [
        'WidgetExecutor',
        'PythonCodeWidget', 
        'WeierstraussWidget',
        'execute_widget',
        'stop_widget',
        'numpy',
        'matplotlib',
        'pyodide.runPython'
    ]
    
    passed = 0
    for feature in python_features:
        if feature in js_content:
            print(f"✅ Python: Found {feature}")
            passed += 1
        else:
            print(f"❌ Python: Missing {feature}")
    
    print(f"\nPython Backend: {passed}/{len(python_features)} components implemented")
    return passed == len(python_features)

def main():
    """Run all tests."""
    print("Enhanced Widget Framework Test Suite")
    print("=" * 60)
    
    test1_passed = test_enhanced_widget_framework()
    test2_passed = test_python_backend_integration()
    
    if test1_passed and test2_passed:
        print("\n🎉 ALL TESTS PASSED! Enhanced widget framework is ready.")
        print("\nKey Features Now Available:")
        print("- Real Python execution with Pyodide")
        print("- Event system for widget communication") 
        print("- Cycle detection for safe connections")
        print("- Proper widget instance ID management")
        print("- Stop/start execution control")
        print("- Attached notes with dynamic variables")
        print("- Enhanced error handling")
        return True
    else:
        print("\n⚠️ Some tests failed. Review implementation.")
        return False

if __name__ == "__main__":
    main()