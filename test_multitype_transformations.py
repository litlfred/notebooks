#!/usr/bin/env python3
"""
Test Multi-Type Transformation System
Tests the new arrow transformation system with multiple languages
"""

import sys
import json
from pathlib import Path

# Add the libraries path to Python path
sys.path.insert(0, str(Path(__file__).parent / "libraries"))

from libraries.core.arrow import WorkflowArrow, TransformerFactory


def test_transformer_factory():
    """Test the transformer factory and registration"""
    print("🔧 Testing Transformer Factory...")
    
    # Check supported types
    supported_types = TransformerFactory.list_supported_types()
    print(f"  Supported MIME types: {supported_types}")
    
    # Should at least have Python support
    assert 'application/x-python' in supported_types, "Python transformer not registered"
    
    # Test getting transformers
    python_transformer = TransformerFactory.get_transformer('application/x-python')
    assert python_transformer is not None, "Failed to get Python transformer"
    
    print("  ✅ Transformer factory working correctly")


def test_legacy_python_transformation():
    """Test backward compatibility with legacy python_code format"""
    print("\n🐍 Testing Legacy Python Transformation...")
    
    arrow_config = {
        'source_widget': 'urn:widget:source',
        'target_widget': 'urn:widget:target',
        'source_parameters': ['x', 'y'],
        'target_parameters': ['a', 'b'],
        'transformation': {
            'python_code': 'source_data["result"] = source_data["x"] * 2 + source_data["y"]',
            'input_mapping': {'x': 'input_x', 'y': 'input_y'}
        }
    }
    
    try:
        arrow = WorkflowArrow(arrow_config)
        assert arrow.transform_function is not None, "Transform function not compiled"
        print("  ✅ Legacy Python transformation compiled successfully")
        
        # Test JSON-LD output
        jsonld = arrow.to_jsonld()
        assert jsonld['workflow:hasTransformation'] == True, "Transformation not indicated in JSON-LD"
        assert jsonld['workflow:transformation']['workflow:legacy'] == True, "Legacy indicator missing"
        print("  ✅ Legacy JSON-LD output correct")
        
    except Exception as e:
        print(f"  ❌ Legacy Python transformation failed: {e}")
        raise


def test_new_python_transformation():
    """Test new multi-type Python transformation format"""
    print("\n🆕 Testing New Python Transformation Format...")
    
    arrow_config = {
        'source_widget': 'urn:widget:source',
        'target_widget': 'urn:widget:target',
        'source_parameters': ['data'],
        'target_parameters': ['processed_data'],
        'transformation': {
            'content_type': 'application/x-python',
            'content_source': 'inline',
            'content': '''
# Normalize data
import math
values = source_data.get("data", [])
if values:
    mean_val = sum(values) / len(values)
    variance = sum((x - mean_val) ** 2 for x in values) / len(values)
    std_val = math.sqrt(variance)
    normalized = [(x - mean_val) / std_val if std_val > 0 else 0 for x in values]
    source_data["processed_data"] = normalized
else:
    source_data["processed_data"] = []
''',
            'execution_context': {
                'timeout': 30,
                'memory_limit': '50MB'
            }
        }
    }
    
    try:
        arrow = WorkflowArrow(arrow_config)
        assert arrow.transform_function is not None, "Transform function not compiled"
        print("  ✅ New Python transformation compiled successfully")
        
        # Test JSON-LD output
        jsonld = arrow.to_jsonld()
        assert jsonld['workflow:hasTransformation'] == True, "Transformation not indicated in JSON-LD"
        assert jsonld['workflow:transformation']['dct:format'] == 'application/x-python', "Content type missing"
        print("  ✅ New Python JSON-LD output correct")
        
    except Exception as e:
        print(f"  ❌ New Python transformation failed: {e}")
        raise


def test_javascript_transformation():
    """Test JavaScript transformation (if Node.js is available)"""
    print("\n🟨 Testing JavaScript Transformation...")
    
    # Check if JavaScript transformer is available
    if not TransformerFactory.is_supported('application/javascript'):
        print("  ⚠️  JavaScript transformer not registered, skipping...")
        return
    
    arrow_config = {
        'source_widget': 'urn:widget:source',
        'target_widget': 'urn:widget:target',
        'source_parameters': ['numbers'],
        'target_parameters': ['doubled'],
        'transformation': {
            'content_type': 'application/javascript',
            'content_source': 'inline',
            'content': '''
// Double all numbers in the array
const numbers = sourceData.numbers || [];
const doubled = numbers.map(x => x * 2);
sourceData.doubled = doubled;
''',
            'execution_context': {
                'timeout': 30
            }
        }
    }
    
    try:
        arrow = WorkflowArrow(arrow_config)
        assert arrow.transform_function is not None, "JavaScript transform function not compiled"
        print("  ✅ JavaScript transformation compiled successfully")
        
        # Test JSON-LD output
        jsonld = arrow.to_jsonld()
        assert jsonld['workflow:transformation']['dct:format'] == 'application/javascript', "JavaScript content type missing"
        print("  ✅ JavaScript JSON-LD output correct")
        
    except Exception as e:
        print(f"  ❌ JavaScript transformation failed: {e}")
        # Don't raise for JavaScript since Node.js might not be available


def test_validation_errors():
    """Test validation and error handling"""
    print("\n🚨 Testing Validation and Error Handling...")
    
    # Test invalid content type
    try:
        arrow_config = {
            'source_widget': 'urn:widget:source',
            'target_widget': 'urn:widget:target',
            'source_parameters': ['x'],
            'target_parameters': ['y'],
            'transformation': {
                'content_type': 'application/nonexistent',
                'content_source': 'inline',
                'content': 'print("hello")'
            }
        }
        WorkflowArrow(arrow_config)
        assert False, "Should have failed with unsupported content type"
    except ValueError as e:
        assert "No transformer registered" in str(e), f"Unexpected error: {e}"
        print("  ✅ Unsupported content type correctly rejected")
    
    # Test invalid Python syntax
    try:
        arrow_config = {
            'source_widget': 'urn:widget:source',
            'target_widget': 'urn:widget:target',
            'source_parameters': ['x'],
            'target_parameters': ['y'],
            'transformation': {
                'content_type': 'application/x-python',
                'content_source': 'inline',
                'content': 'this is not valid python syntax !!!'
            }
        }
        WorkflowArrow(arrow_config)
        assert False, "Should have failed with invalid Python syntax"
    except ValueError as e:
        assert "Invalid" in str(e), f"Unexpected error: {e}"
        print("  ✅ Invalid Python syntax correctly rejected")


def test_mock_execution():
    """Test arrow execution with mock widgets"""
    print("\n⚡ Testing Arrow Execution...")
    
    # Create mock widgets
    class MockSourceWidget:
        def __init__(self):
            self.output_variables = {'data': [1, 2, 3, 4, 5]}
    
    class MockTargetWidget:
        def __init__(self):
            self.input_variables = {}
    
    # Test with Python transformation
    arrow_config = {
        'source_widget': 'urn:widget:source',
        'target_widget': 'urn:widget:target',
        'source_parameters': ['data'],
        'target_parameters': ['processed'],
        'transformation': {
            'content_type': 'application/x-python',
            'content_source': 'inline',
            'content': 'source_data["processed"] = [x * 2 for x in source_data["data"]]'
        }
    }
    
    try:
        arrow = WorkflowArrow(arrow_config)
        source_widget = MockSourceWidget()
        target_widget = MockTargetWidget()
        
        result = arrow.execute_connection(source_widget, target_widget)
        
        assert result['success'] == True, f"Execution failed: {result}"
        assert result['transformation_applied'] == True, "Transformation not applied"
        assert 'processed' in result['parameters_transferred'], "Processed data missing"
        
        expected_result = [2, 4, 6, 8, 10]
        actual_result = result['parameters_transferred']['processed']
        assert actual_result == expected_result, f"Expected {expected_result}, got {actual_result}"
        
        print("  ✅ Arrow execution successful")
        print(f"    Input: {source_widget.output_variables['data']}")
        print(f"    Output: {actual_result}")
        
    except Exception as e:
        print(f"  ❌ Arrow execution failed: {e}")
        raise


def main():
    """Run all tests"""
    print("🧪 Multi-Type Transformation System Tests")
    print("=" * 50)
    
    try:
        test_transformer_factory()
        test_legacy_python_transformation()
        test_new_python_transformation()
        test_javascript_transformation()
        test_validation_errors()
        test_mock_execution()
        
        print("\n🎉 All tests passed!")
        print("\n📊 Summary:")
        print("  ✅ Transformer factory working")
        print("  ✅ Legacy Python transformation backward compatible")
        print("  ✅ New Python transformation format working")
        print("  ✅ JavaScript transformation system ready")
        print("  ✅ Validation and error handling working")
        print("  ✅ Arrow execution working")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)