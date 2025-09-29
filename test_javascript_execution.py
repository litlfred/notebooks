#!/usr/bin/env python3
"""
Test JavaScript Transformation Execution
Tests that JavaScript transformations actually execute correctly
"""

import sys
from pathlib import Path

# Add the libraries path to Python path
sys.path.insert(0, str(Path(__file__).parent / "libraries"))

from libraries.core.arrow import WorkflowArrow


def test_javascript_execution():
    """Test JavaScript transformation execution"""
    print("🟨 Testing JavaScript Transformation Execution...")
    
    # Create mock widgets
    class MockSourceWidget:
        def __init__(self):
            self.output_variables = {
                'numbers': [1, 2, 3, 4, 5],
                'multiplier': 3
            }
    
    class MockTargetWidget:
        def __init__(self):
            self.input_variables = {}
    
    # Test with JavaScript transformation
    arrow_config = {
        'source_widget': 'urn:widget:source',
        'target_widget': 'urn:widget:target',
        'source_parameters': ['numbers', 'multiplier'],
        'target_parameters': ['result'],
        'transformation': {
            'content_type': 'application/javascript',
            'content_source': 'inline',
            'content': '''
// Multiply each number by the multiplier
const numbers = sourceData.numbers || [];
const multiplier = sourceData.multiplier || 1;

const result = numbers.map(x => x * multiplier);
sourceData.result = result;

console.log("JavaScript transformation executed successfully");
''',
            'execution_context': {
                'timeout': 30
            }
        }
    }
    
    try:
        arrow = WorkflowArrow(arrow_config)
        source_widget = MockSourceWidget()
        target_widget = MockTargetWidget()
        
        result = arrow.execute_connection(source_widget, target_widget)
        
        print(f"  Execution result: {result['success']}")
        if result['success']:
            transformed_data = result['parameters_transferred']
            print(f"  Input numbers: {source_widget.output_variables['numbers']}")
            print(f"  Multiplier: {source_widget.output_variables['multiplier']}")
            print(f"  Output result: {transformed_data.get('result', 'Not found')}")
            
            expected = [3, 6, 9, 12, 15]  # [1,2,3,4,5] * 3
            actual = transformed_data.get('result', [])
            
            if actual == expected:
                print("  ✅ JavaScript transformation executed correctly")
                return True
            else:
                print(f"  ❌ Unexpected result. Expected {expected}, got {actual}")
                return False
        else:
            print(f"  ❌ Execution failed: {result.get('error_message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"  ❌ JavaScript transformation test failed: {e}")
        return False


def main():
    """Run JavaScript execution test"""
    print("🧪 JavaScript Transformation Execution Test")
    print("=" * 50)
    
    success = test_javascript_execution()
    
    if success:
        print("\n🎉 JavaScript transformation execution test passed!")
    else:
        print("\n❌ JavaScript transformation execution test failed!")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)