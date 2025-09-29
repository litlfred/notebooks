#!/usr/bin/env python3
"""
Test Jupyter notebook import functionality
"""

import json
import sys
import os

# Add library path
sys.path.append(os.path.join(os.path.dirname(__file__), 'libraries', 'core', 'jupyter-cell'))

from jupyter_importer import JupyterNotebookImporter


def test_jupyter_importer():
    """Test the Jupyter notebook importer with a sample notebook"""
    
    # Create sample Jupyter notebook
    sample_notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# Sample Notebook\n",
                    "\n",
                    "This is a test notebook with markdown and code cells."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": 1,
                "metadata": {},
                "outputs": [
                    {
                        "output_type": "stream",
                        "name": "stdout",
                        "text": ["Hello, World!\n"]
                    }
                ],
                "source": [
                    "print(\"Hello, World!\")"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": 2,
                "metadata": {},
                "outputs": [
                    {
                        "output_type": "execute_result",
                        "execution_count": 2,
                        "data": {
                            "text/plain": ["42"]
                        },
                        "metadata": {}
                    }
                ],
                "source": [
                    "6 * 7"
                ]
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.8.0"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 2
    }
    
    print("Testing Jupyter notebook importer...")
    
    # Test validation
    importer = JupyterNotebookImporter()
    
    if not importer.validate_notebook_format(sample_notebook):
        print("❌ Notebook validation failed")
        return False
    
    print("✅ Notebook validation passed")
    
    # Test preview generation
    preview = importer.get_notebook_preview(sample_notebook)
    
    if not preview['valid']:
        print("❌ Preview generation failed")
        return False
    
    print("✅ Preview generation passed")
    print(f"   - Title: {preview['title']}")
    print(f"   - Language: {preview['language']}")
    print(f"   - Total cells: {preview['total_cells']}")
    print(f"   - Cell types: {preview['cell_types']}")
    
    # Test import
    result = importer.import_notebook(sample_notebook, 'import')
    
    if not result or '@graph' not in result:
        print("❌ Import failed")
        return False
    
    print("✅ Import successful")
    
    # Validate result structure
    graph = result['@graph']
    widgets = [item for item in graph if 'widget:instance' in item.get('@type', [])]
    connections = [item for item in graph if 'workflow:Connection' in item.get('@type', [])]
    
    print(f"   - Generated {len(widgets)} widgets")
    print(f"   - Generated {len(connections)} connections")
    
    # Check widget types
    widget_types = {}
    for widget in widgets:
        widget_type = widget.get('widget:type', 'unknown')
        widget_types[widget_type] = widget_types.get(widget_type, 0) + 1
    
    print(f"   - Widget types: {widget_types}")
    
    # Validate expected widget types
    expected_types = {'jupyter-markdown-cell': 1, 'jupyter-code-cell': 2}
    for expected_type, expected_count in expected_types.items():
        if widget_types.get(expected_type, 0) != expected_count:
            print(f"❌ Expected {expected_count} {expected_type} widgets, got {widget_types.get(expected_type, 0)}")
            return False
    
    print("✅ All widget types correct")
    
    # Check for sequential connections
    if len(connections) != len(widgets) - 1:
        print(f"❌ Expected {len(widgets) - 1} connections, got {len(connections)}")
        return False
    
    print("✅ Sequential connections correct")
    
    return True


def test_file_import():
    """Test importing from file content"""
    
    sample_content = json.dumps({
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": ["# Test from file"]
            }
        ],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 2
    })
    
    importer = JupyterNotebookImporter()
    result = importer.import_from_file(sample_content, 'test.ipynb')
    
    if not result:
        print("❌ File import failed")
        return False
    
    print("✅ File import successful")
    return True


def main():
    """Run all tests"""
    print("🚀 Testing Jupyter notebook import functionality\n")
    
    tests_passed = 0
    total_tests = 2
    
    if test_jupyter_importer():
        tests_passed += 1
    
    print()
    
    if test_file_import():
        tests_passed += 1
    
    print(f"\n📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Jupyter import functionality is working.")
        return True
    else:
        print("⚠️ Some tests failed.")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)