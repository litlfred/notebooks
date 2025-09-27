# Widget Framework Migration Guide

## Overview

This guide provides a detailed migration plan for transitioning existing widgets to the new JSON schema-based widget framework. The migration process is designed to be incremental and backward-compatible.

## Current Widget Analysis

### Existing Widget Types

Based on the current implementation in `docs/weierstrass-playground/`, the following widgets are already partially compliant:

| Widget ID | Status | Migration Complexity | Notes |
|-----------|--------|---------------------|-------|
| `markdown-note` | ✅ Compliant | Low | Already has proper schema |
| `python-code` | ✅ Compliant | Low | Schema matches framework |
| `wp-two-panel` | ⚠️ Partial | Medium | Need execution wrapper |
| `wp-three-panel` | ⚠️ Partial | Medium | Need execution wrapper |
| `wp-five-panel` | ⚠️ Partial | Medium | Need execution wrapper |
| `wp-trajectories` | ⚠️ Partial | Medium | Need execution wrapper |
| `wp-lattice` | ⚠️ Partial | High | Complex parameters |
| `wp-poles` | ⚠️ Partial | Medium | Need execution wrapper |
| `wp-contours` | ⚠️ Partial | Medium | Need execution wrapper |
| `data-plot` | ✅ Compliant | Low | Already has proper schema |
| `data-generator` | ✅ Compliant | Low | Already has proper schema |

## Migration Phases

### Phase 1: Framework Preparation (Week 1)
**Status**: ✅ Complete

- [x] Document framework architecture
- [x] Create JSON schema specification
- [x] Implement sticky-note widget as example
- [x] Update widget-schemas.json with sticky-note

### Phase 2: Execution Engine Enhancement (Week 2)

#### 2.1 Update WidgetExecutor Base Class
```python
# Current implementation in widget_executor.py needs enhancement
class WidgetExecutor:
    def __init__(self, widget_schema: Dict[str, Any]):
        self.schema = widget_schema
        self.id = widget_schema['id']
        self.name = widget_schema['name']
        self.input_schema = widget_schema['input_schema']
        self.output_schema = widget_schema['output_schema']
        
    def validate_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        # Enhanced validation with detailed error reporting
        pass
        
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        # Standardized execution with error handling
        pass
```

#### 2.2 Create Widget Factory
```python
def create_widget(widget_type: str, schemas: Dict[str, Any]) -> WidgetExecutor:
    """Factory function to create widget instances"""
    if widget_type not in schemas['widget-schemas']:
        raise ValueError(f"Unknown widget type: {widget_type}")
    
    schema = schemas['widget-schemas'][widget_type]
    
    # Map widget types to implementation classes
    widget_classes = {
        'sticky-note': StickyNoteWidget,
        'markdown-note': MarkdownWidget,
        'python-code': PythonWidget,
        'wp-two-panel': WeierstrassTwoPanelWidget,
        # ... other mappings
    }
    
    widget_class = widget_classes.get(widget_type, WidgetExecutor)
    return widget_class(schema)
```

### Phase 3: Individual Widget Migration (Weeks 3-4)

#### 3.1 Weierstrass Widgets Migration

**Current Structure:**
```python
class WeierstrassTwoPanelWidget(WidgetExecutor):
    def _execute_impl(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        p = validated_input['p']
        q = validated_input['q'] 
        N = validated_input['N']
        # ... existing implementation
        return {
            'plot_data': {
                'image_base64': f'two_panel_plot_p{p}_q{q}',
                'width': 800,
                'height': 400
            }
        }
```

**Migration Steps:**
1. ✅ Schema already compliant in `widget-schemas.json`
2. Wrap existing computation in WidgetExecutor framework
3. Add proper error handling and validation
4. Ensure output matches output schema
5. Add unit tests

#### 3.2 Python Code Widget Enhancement

**Current Implementation:**
```python
class PythonWidget(WidgetExecutor):
    def _execute_impl(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        code = validated_input['code']
        # ... execution logic
```

**Required Enhancements:**
- Add execution timeout handling
- Improve variable passing between widgets
- Enhanced error reporting
- Stdout/stderr capture

#### 3.3 Data Widgets Enhancement

**Migration Tasks:**
- Standardize output format for data-plot widget
- Add more data generation options to data-generator
- Implement proper data validation

### Phase 4: UI Framework Integration (Week 5)

#### 4.1 Dynamic Form Generation Enhancement

**Current JavaScript (board-app.js):**
```javascript
function generateSchemaForm(inputSchema, currentConfig) {
    // Current implementation needs enhancement for:
    // - Better UI widget type support
    // - Validation feedback
    // - Accessibility features
}
```

**Enhancement Plan:**
1. Add support for all UI widget types from specification
2. Implement real-time validation feedback
3. Add accessibility features (ARIA labels, keyboard navigation)
4. Improve mobile responsiveness

#### 4.2 Connection System Enhancement

**Current Implementation:**
```javascript
connectWidgets(sourceId, targetId, outputPath, inputPath) {
    // Basic connection support exists
}
```

**Required Enhancements:**
- Visual connection drawing with arrows
- Connection validation (type checking)
- ETL script support for data transformation
- Connection persistence in board state

### Phase 5: Advanced Features (Week 6-7)

#### 5.1 Attached Notes System

**Implementation Plan:**
```javascript
class AttachedNote {
    constructor(widgetId) {
        this.widgetId = widgetId;
        this.content = "# Notes\n\nWidget-specific documentation...";
        this.visible = true;
        this.variables = new Map(); // Dynamic variables from widget execution
    }
    
    updateVariables(inputData, outputData) {
        // Update dynamic variables from widget execution
    }
    
    renderWithVariables() {
        // Render markdown with variable substitution
    }
}
```

#### 5.2 Event System Implementation

**Event Types:**
- `widget.input.changed`
- `widget.output.generated` 
- `widget.status.changed`
- `widget.connection.added/removed`

**Implementation:**
```javascript
class WidgetEventSystem {
    constructor() {
        this.listeners = new Map();
    }
    
    addEventListener(eventType, callback) {
        // Event registration
    }
    
    fireEvent(eventType, data) {
        // Event emission with proper error handling
    }
}
```

#### 5.3 Accessibility Enhancements

**Required Features:**
- Full keyboard navigation
- Screen reader support with ARIA labels
- High contrast theme support
- Focus management for modal dialogs
- Alternative text for visualizations

### Phase 6: Testing and Documentation (Week 8)

#### 6.1 Comprehensive Testing

**Test Categories:**
1. **Unit Tests**: Individual widget execution
2. **Integration Tests**: Widget connections and dependencies
3. **UI Tests**: Form generation and interaction
4. **Accessibility Tests**: Screen reader and keyboard navigation
5. **Performance Tests**: Large board with many widgets

**Test Structure:**
```python
def test_sticky_note_widget():
    widget = create_sticky_note_widget()
    result = widget.execute({"content": "Test content"})
    assert result["success"] is True
    assert "Test content" in result["rendered_html"]

def test_widget_connection():
    # Test data flow between connected widgets
    pass

def test_form_generation():
    # Test UI generation from schema
    pass
```

#### 6.2 Documentation Updates

**Documentation Tasks:**
- ✅ Complete framework documentation
- ✅ JSON schema specification
- User guide with examples
- Developer API reference
- Migration guide for custom widgets
- Troubleshooting guide

## Migration Checklist

### For Existing Widgets

- [ ] **Schema Compliance**: Verify widget schema matches specification
- [ ] **Execution Wrapper**: Implement WidgetExecutor subclass
- [ ] **Input Validation**: Add proper parameter validation
- [ ] **Output Standardization**: Ensure output matches schema
- [ ] **Error Handling**: Implement graceful error handling
- [ ] **Testing**: Add unit tests for widget functionality
- [ ] **Documentation**: Document widget parameters and usage

### For Framework Core

- [ ] **Enhanced Validation**: Improve schema validation with detailed errors
- [ ] **Widget Factory**: Implement dynamic widget creation
- [ ] **Connection System**: Visual connection interface with arrows
- [ ] **Event System**: Widget communication and change notifications
- [ ] **Attached Notes**: Per-widget documentation system
- [ ] **Accessibility**: Full keyboard and screen reader support
- [ ] **Internationalization**: Multi-language support framework
- [ ] **Performance**: Optimize for large boards with many widgets

### For UI Components

- [ ] **Form Generation**: Enhanced dynamic form generation
- [ ] **Widget Library**: Improved widget palette with search
- [ ] **Board Management**: Save/load board configurations
- [ ] **Theme System**: Dark/light mode with custom themes
- [ ] **Mobile Support**: Responsive design for tablets/phones
- [ ] **Export/Import**: Board and widget configuration persistence

## Risk Assessment and Mitigation

### High Risk Areas

1. **Breaking Changes to Existing Widgets**
   - **Risk**: Users lose existing widget configurations
   - **Mitigation**: Maintain backward compatibility, provide migration tools

2. **Performance Regression**
   - **Risk**: New framework adds overhead
   - **Mitigation**: Performance testing, optimization, lazy loading

3. **Complexity for Widget Authors**
   - **Risk**: Framework becomes too complex for simple widgets
   - **Mitigation**: Provide simple examples, good documentation, templates

### Medium Risk Areas

1. **Browser Compatibility**
   - **Risk**: New features don't work in older browsers
   - **Mitigation**: Progressive enhancement, polyfills where needed

2. **Schema Evolution**
   - **Risk**: Future changes break existing widgets
   - **Mitigation**: Semantic versioning, deprecation warnings

## Success Criteria

### Technical Metrics
- ✅ All existing widgets migrated without functionality loss
- ✅ Framework documentation complete and comprehensive
- ✅ Sticky note widget implemented as simplest example
- 100% backward compatibility maintained
- < 10% performance regression on existing functionality
- All accessibility standards (WCAG 2.1 AA) met

### User Experience Metrics
- Improved widget creation workflow (< 5 steps to create new widget)
- Enhanced connection interface with visual feedback
- Better error messages with actionable guidance
- Mobile-friendly responsive design

### Developer Experience Metrics
- Complete API documentation with examples
- Simple widget template reduces development time by 50%
- Comprehensive test suite with > 90% coverage
- Clear migration path for custom widgets

## Timeline Summary

| Phase | Duration | Key Deliverables | Status |
|-------|----------|------------------|--------|
| 1 | Week 1 | Framework docs, JSON schema spec, sticky-note widget | ✅ Complete |
| 2 | Week 2 | Enhanced execution engine, widget factory | 🔄 Next |
| 3 | Weeks 3-4 | Migrate all existing widgets | 📋 Planned |
| 4 | Week 5 | UI enhancements, connection system | 📋 Planned |
| 5 | Weeks 6-7 | Advanced features (notes, events, a11y) | 📋 Planned |
| 6 | Week 8 | Testing, final documentation | 📋 Planned |

**Total Estimated Duration**: 8 weeks
**Risk Buffer**: +2 weeks for unforeseen issues

## Getting Started with Migration

### For Widget Authors

1. **Review Documentation**: Read the widget framework documentation
2. **Check Schema**: Validate your widget against JSON schema specification  
3. **Test Sticky Note**: Run the sticky note example to understand the pattern
4. **Create Wrapper**: Implement WidgetExecutor subclass for your widget
5. **Add Tests**: Write unit tests for your widget functionality
6. **Submit PR**: Submit migration pull request with documentation

### For Framework Contributors

1. **Understand Current State**: Review existing implementation in weierstrass-playground
2. **Pick a Phase**: Choose a migration phase to work on
3. **Follow Patterns**: Use sticky note widget as implementation pattern
4. **Test Thoroughly**: Ensure no regression in existing functionality
5. **Document Changes**: Update documentation for any new features
6. **Coordinate**: Work with other contributors to avoid conflicts

This migration guide ensures a smooth transition to the new widget framework while maintaining all existing functionality and improving the overall user and developer experience.