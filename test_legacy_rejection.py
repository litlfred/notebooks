#!/usr/bin/env python3
"""
Test that legacy format is rejected
Tests that the old python_code format no longer works
"""

import sys
from pathlib import Path

# Add the libraries path to Python path
sys.path.insert(0, str(Path(__file__).parent / "libraries"))

from libraries.core.arrow import WorkflowArrow


def test_legacy_format_rejected():
    """Test that legacy python_code format is rejected"""
    print("🚫 Testing that legacy format is rejected...")
    
    arrow_config = {
        'source_widget': 'urn:widget:source',
        'target_widget': 'urn:widget:target',
        'source_parameters': ['x'],
        'target_parameters': ['y'],
        'transformation': {
            'python_code': 'source_data["result"] = source_data["x"] * 2'
        }
    }
    
    try:
        WorkflowArrow(arrow_config)
        print("  ❌ Legacy format should have been rejected!")
        return False
    except ValueError as e:
        if "content_type is required" in str(e):
            print("  ✅ Legacy format properly rejected")
            print(f"    Error: {e}")
            return True
        else:
            print(f"  ❌ Unexpected error: {e}")
            return False
    except Exception as e:
        print(f"  ❌ Unexpected exception: {e}")
        return False


def main():
    """Test legacy format rejection"""
    print("🧪 Legacy Format Rejection Test")
    print("=" * 40)
    
    success = test_legacy_format_rejected()
    
    if success:
        print("\n🎉 Legacy format properly rejected!")
    else:
        print("\n❌ Legacy format rejection test failed!")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)