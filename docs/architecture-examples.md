# Widget Framework Architecture and Examples

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                     │
├─────────────────────────────────────────────────────────────┤
│  Widget Library  │  Blackboard Canvas  │  Configuration UI  │
│  - Drag & Drop   │  - Visual Layout    │  - Schema Forms   │
│  - Search/Filter │  - Connections      │  - Real-time Val. │
│  - Categories    │  - Multi-selection  │  - Help System    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Application Layer                         │
├─────────────────────────────────────────────────────────────┤
│  MathematicalBoard │  WidgetGraph     │  EventSystem       │
│  - Widget Mgmt     │  - Dependencies  │  - Change Events   │
│  - Layout Engine   │  - Execution     │  - Error Handling  │
│  - State Mgmt      │  - Caching       │  - Notifications   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Widget Framework Layer                     │
├─────────────────────────────────────────────────────────────┤
│  WidgetExecutor    │  Schema Engine   │  Connection Mgmt   │
│  - Base Classes    │  - Validation    │  - Data Flow       │
│  - Life Cycle      │  - UI Generation │  - Type Checking   │
│  - Error Handling  │  - Defaults      │  - ETL Scripts     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Execution Layer                           │
├─────────────────────────────────────────────────────────────┤
│  Python Runtime    │  JavaScript VM   │  Data Processing   │
│  - Code Execution  │  - UI Logic      │  - Transformations │
│  - Library Access  │  - Event Loops   │  - Streaming       │
│  - Sandboxing      │  - DOM Updates   │  - Caching         │
└─────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

```
User Action (Widget Placement)
       │
       ▼
   UI Layer (board-app.js)
       │
       ├─→ Generate Widget Instance
       ├─→ Load Schema Definition  
       ├─→ Create DOM Elements
       └─→ Register Event Handlers
       │
       ▼
   Widget Framework
       │
       ├─→ Validate Configuration
       ├─→ Generate Input Form
       └─→ Setup Execution Context
       │
       ▼
   Execution on User Trigger
       │
       ├─→ Python Script Execution
       ├─→ Output Validation
       ├─→ UI Update
       └─→ Event Notification
```

### Data Flow Architecture

```
Input Data → Schema Validation → Widget Execution → Output Processing → UI Update
     │              │                   │                  │             │
     │              ├─ Type Check       ├─ Python Runtime  ├─ Format     ├─ Render  
     │              ├─ Apply Defaults   ├─ Error Capture   ├─ Cache      ├─ Connect
     │              └─ Range Check      └─ Result Return   └─ Notify     └─ Event Fire
```

## Implementation Examples

### 1. Complete Widget Implementation

#### Sticky Note Widget (Simplest Example)

**Schema Definition (widget-schemas.json):**
```json
{
  "sticky-note": {
    "id": "sticky-note",
    "name": "Sticky Note",
    "description": "Simple markdown note widget",
    "category": "content",
    "icon": "📝",
    "input_schema": {
      "type": "object",
      "properties": {
        "content": {
          "type": "string", 
          "description": "Markdown content",
          "default": "# New Note\n\nEdit to add content...",
          "ui:widget": "textarea",
          "ui:placeholder": "Enter markdown content..."
        },
        "show_note": {
          "type": "boolean",
          "description": "Show/hide note",
          "default": true
        }
      },
      "required": ["content"]
    },
    "output_schema": {
      "type": "object",
      "properties": {
        "success": {"type": "boolean"},
        "rendered_html": {"type": "string"},
        "metadata": {
          "type": "object",
          "properties": {
            "visible": {"type": "boolean"},
            "content_length": {"type": "integer"}
          }
        }
      }
    },
    "python_script": "widgets/sticky_note.py"
  }
}
```

**Python Implementation (widgets/sticky_note.py):**
```python
class StickyNoteWidget(WidgetExecutor):
    def _execute_impl(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        content = validated_input.get('content', '')
        show_note = validated_input.get('show_note', True)
        
        if not show_note:
            return {
                'success': True,
                'rendered_html': '<div class="note-hidden">Hidden</div>',
                'metadata': {'visible': False, 'content_length': len(content)}
            }
        
        html = self.render_markdown(content)
        return {
            'success': True,
            'rendered_html': f'<div class="sticky-note">{html}</div>',
            'metadata': {'visible': True, 'content_length': len(content)}
        }
```

### 2. Advanced Widget with Complex Schema

#### Data Visualization Widget

**Schema Definition:**
```json
{
  "advanced-plot": {
    "id": "advanced-plot",
    "name": "Advanced Data Plot",
    "description": "Multi-series data visualization with customization",
    "category": "visualization", 
    "icon": "📈",
    "input_schema": {
      "type": "object",
      "properties": {
        "data": {
          "type": "object",
          "description": "Plot data series",
          "properties": {
            "series": {
              "type": "array",
              "items": {
                "type": "object", 
                "properties": {
                  "name": {"type": "string", "default": "Series 1"},
                  "x": {"type": "array", "items": {"type": "number"}},
                  "y": {"type": "array", "items": {"type": "number"}},
                  "type": {"enum": ["line", "scatter", "bar"], "default": "line"},
                  "color": {"type": "string", "format": "color", "default": "#1f77b4"}
                },
                "required": ["x", "y"]
              },
              "minItems": 1,
              "default": [{"name": "Series 1", "x": [1,2,3], "y": [1,4,9]}]
            }
          },
          "required": ["series"]
        },
        "layout": {
          "type": "object",
          "properties": {
            "title": {"type": "string", "default": "Data Plot"},
            "xlabel": {"type": "string", "default": "X Axis"},
            "ylabel": {"type": "string", "default": "Y Axis"},
            "width": {"type": "integer", "minimum": 200, "maximum": 1200, "default": 800},
            "height": {"type": "integer", "minimum": 200, "maximum": 800, "default": 600},
            "grid": {"type": "boolean", "default": true},
            "legend": {"type": "boolean", "default": true}
          }
        },
        "style": {
          "type": "object",
          "properties": {
            "theme": {"enum": ["default", "dark", "minimal"], "default": "default"},
            "colormap": {"enum": ["tab10", "viridis", "plasma"], "default": "tab10"},
            "font_size": {"type": "integer", "minimum": 8, "maximum": 24, "default": 12}
          }
        }
      },
      "required": ["data"]
    },
    "output_schema": {
      "type": "object",
      "properties": {
        "success": {"type": "boolean"},
        "plot_image": {
          "type": "object",
          "properties": {
            "image_base64": {"type": "string"},
            "width": {"type": "integer"},
            "height": {"type": "integer"},
            "mime_type": {"type": "string"}
          }
        },
        "statistics": {
          "type": "object",
          "properties": {
            "series_count": {"type": "integer"},
            "total_points": {"type": "integer"},
            "x_range": {"type": "array", "items": {"type": "number"}},
            "y_range": {"type": "array", "items": {"type": "number"}}
          }
        },
        "metadata": {
          "type": "object",
          "properties": {
            "execution_time": {"type": "number"},
            "generated_at": {"type": "string"}
          }
        }
      }
    },
    "python_script": "widgets/advanced_plot.py"
  }
}
```

### 3. Widget with Dependencies

#### Statistical Analysis Widget (depends on data source)

**Connection Example:**
```javascript
// Connect data-generator output to statistical-analysis input
boardApp.connectWidgets(
  "data-gen-1",           // Source widget ID
  "stats-analysis-1",     // Target widget ID  
  "data.output",          // Output path from source
  "data.input"            // Input path to target
);
```

**ETL Script for Data Transformation:**
```python
# Custom transformation between widgets
def transform_data(source_output, target_input_schema):
    """Transform data from source format to target format"""
    source_data = source_output.get('data', {})
    
    # Extract arrays
    x_values = source_data.get('x', [])
    y_values = source_data.get('y', [])
    
    # Transform to target format
    return {
        'dataset': {
            'x_data': x_values,
            'y_data': y_values,
            'sample_size': len(x_values)
        }
    }
```

### 4. Widget with Attached Notes

#### Enhanced Widget with Documentation

**JavaScript Implementation:**
```javascript
class AttachedNote {
    constructor(widgetId, widget) {
        this.widgetId = widgetId;
        this.widget = widget;
        this.content = this.getDefaultNoteContent();
        this.visible = true;
        this.lastUpdate = new Date();
    }
    
    getDefaultNoteContent() {
        return `# ${this.widget.title} Notes

## Configuration
- **Widget Type**: ${this.widget.type}
- **Created**: {{timestamp}}
- **Last Modified**: {{last_modified}}

## Current Settings
{{#each config}}
- **{{@key}}**: {{this}}
{{/each}}

## Results Summary
{{#if lastOutput}}
- **Status**: {{lastOutput.success}}
- **Execution Time**: {{lastOutput.metadata.execution_time}}ms
{{/if}}

## Additional Notes
Add your own notes and observations here...`;
    }
    
    updateVariables() {
        const variables = {
            timestamp: this.widget.createdAt || new Date().toISOString(),
            last_modified: new Date().toISOString(),
            config: this.widget.config,
            lastOutput: this.widget.lastOutput
        };
        
        this.renderedContent = this.renderTemplate(this.content, variables);
    }
    
    renderTemplate(template, variables) {
        // Simple template rendering with variable substitution
        return template.replace(/\{\{(\w+)\}\}/g, (match, key) => {
            return variables[key] || match;
        });
    }
}
```

### 5. Accessibility Implementation

#### Keyboard Navigation and Screen Reader Support

**HTML Structure with ARIA:**
```html
<div class="widget-container" 
     role="application" 
     aria-label="Mathematical Widget"
     tabindex="0"
     data-widget-id="widget-1">
  
  <header class="widget-header" role="banner">
    <h3 id="widget-title-1">Data Plot Widget</h3>
    <div class="widget-controls" role="toolbar" aria-labelledby="widget-title-1">
      <button class="btn-run" 
              aria-label="Execute widget"
              title="Run this widget (Ctrl+Enter)">
        <span aria-hidden="true">▶</span>
        <span class="sr-only">Run</span>
      </button>
      <button class="btn-edit" 
              aria-label="Edit widget configuration"
              title="Configure widget (Ctrl+E)">
        <span aria-hidden="true">⚙</span>
        <span class="sr-only">Configure</span>
      </button>
    </div>
  </header>
  
  <main class="widget-content" role="main">
    <div class="widget-output" 
         role="img" 
         aria-labelledby="output-description-1">
      <!-- Widget output content -->
    </div>
    <div id="output-description-1" class="sr-only">
      Data plot showing relationship between X and Y variables with 100 data points
    </div>
  </main>
  
  <footer class="widget-status" role="status" aria-live="polite">
    <span class="status-text">Ready</span>
    <span class="execution-time">Last run: 150ms</span>
  </footer>
</div>
```

**Keyboard Event Handlers:**
```javascript
class AccessibleWidget {
    setupKeyboardNavigation() {
        this.element.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch(e.key) {
                    case 'Enter':
                        e.preventDefault();
                        this.executeWidget();
                        this.announceToScreenReader('Widget executed');
                        break;
                    case 'e':
                        e.preventDefault(); 
                        this.openConfiguration();
                        break;
                    case 'd':
                        e.preventDefault();
                        this.deleteWidget();
                        break;
                }
            }
        });
    }
    
    announceToScreenReader(message) {
        const announcement = document.createElement('div');
        announcement.setAttribute('role', 'status');
        announcement.setAttribute('aria-live', 'polite');
        announcement.className = 'sr-only';
        announcement.textContent = message;
        document.body.appendChild(announcement);
        
        setTimeout(() => document.body.removeChild(announcement), 1000);
    }
}
```

### 6. Event System Implementation

#### Widget Communication Events

**Event System Design:**
```javascript
class WidgetEventSystem extends EventTarget {
    constructor() {
        super();
        this.eventLog = [];
    }
    
    fireWidgetEvent(eventType, widgetId, data) {
        const event = new CustomEvent(`widget:${eventType}`, {
            detail: {
                widgetId,
                timestamp: Date.now(),
                data
            }
        });
        
        this.eventLog.push(event.detail);
        this.dispatchEvent(event);
    }
    
    onWidgetInputChange(widgetId, inputData) {
        this.fireWidgetEvent('input.changed', widgetId, inputData);
    }
    
    onWidgetOutputGenerated(widgetId, outputData) {
        this.fireWidgetEvent('output.generated', widgetId, outputData);
    }
    
    onWidgetStatusChange(widgetId, status) {
        this.fireWidgetEvent('status.changed', widgetId, { status });
    }
}
```

**Event Listeners:**
```javascript
// Global event listeners for widget coordination
eventSystem.addEventListener('widget:output.generated', (e) => {
    const { widgetId, data } = e.detail;
    
    // Find dependent widgets and trigger updates
    const dependentWidgets = findDependentWidgets(widgetId);
    dependentWidgets.forEach(widget => {
        updateWidgetInputFromConnection(widget, data);
        scheduleWidgetExecution(widget.id);
    });
});

// Error propagation
eventSystem.addEventListener('widget:error', (e) => {
    const { widgetId, error } = e.detail;
    
    // Mark dependent widgets as stale
    const dependentWidgets = findDependentWidgets(widgetId);
    dependentWidgets.forEach(widget => {
        widget.status = 'stale';
        widget.lastError = `Dependency error from ${widgetId}: ${error}`;
    });
});
```

### 7. Internationalization Support

#### Multi-language Widget Framework

**Language Resource Structure:**
```javascript
const i18nResources = {
    en: {
        widgets: {
            'sticky-note': {
                name: 'Sticky Note',
                description: 'Simple markdown note widget',
                properties: {
                    content: {
                        label: 'Content',
                        help: 'Enter your markdown content here'
                    },
                    show_note: {
                        label: 'Show Note',
                        help: 'Toggle note visibility'
                    }
                }
            }
        },
        ui: {
            run: 'Run',
            edit: 'Edit', 
            delete: 'Delete',
            configure: 'Configure',
            save: 'Save',
            cancel: 'Cancel'
        }
    },
    es: {
        widgets: {
            'sticky-note': {
                name: 'Nota Adhesiva',
                description: 'Widget simple de notas en markdown',
                properties: {
                    content: {
                        label: 'Contenido',
                        help: 'Ingresa tu contenido en markdown aquí'
                    }
                }
            }
        }
    }
};
```

**UI Generation with i18n:**
```javascript
function generateLocalizedForm(schema, widgetType, locale = 'en') {
    const resources = i18nResources[locale];
    const widgetResources = resources.widgets[widgetType] || {};
    
    return Object.entries(schema.properties).map(([key, propSchema]) => {
        const localizedProp = widgetResources.properties?.[key] || {};
        const label = localizedProp.label || propSchema.description || key;
        const help = localizedProp.help || '';
        
        return `
            <div class="form-field">
                <label for="${key}">${label}</label>
                <input id="${key}" type="text" placeholder="${help}">
                ${help ? `<small class="help-text">${help}</small>` : ''}
            </div>
        `;
    }).join('');
}
```

### 8. Performance Optimization

#### Lazy Loading and Caching

**Widget Loading Strategy:**
```javascript
class OptimizedWidgetManager {
    constructor() {
        this.widgetCache = new Map();
        this.executionCache = new Map();
        this.loadingQueue = [];
    }
    
    async loadWidget(widgetType) {
        if (this.widgetCache.has(widgetType)) {
            return this.widgetCache.get(widgetType);
        }
        
        // Lazy load widget schema and implementation
        const [schema, implementation] = await Promise.all([
            this.loadWidgetSchema(widgetType),
            this.loadWidgetImplementation(widgetType)
        ]);
        
        const widget = { schema, implementation };
        this.widgetCache.set(widgetType, widget);
        return widget;
    }
    
    async executeWidgetWithCaching(widgetId, inputData) {
        const cacheKey = this.generateCacheKey(widgetId, inputData);
        
        if (this.executionCache.has(cacheKey)) {
            const cached = this.executionCache.get(cacheKey);
            if (Date.now() - cached.timestamp < 60000) { // 1 minute cache
                return cached.result;
            }
        }
        
        const result = await this.executeWidget(widgetId, inputData);
        this.executionCache.set(cacheKey, {
            result,
            timestamp: Date.now()
        });
        
        return result;
    }
}
```

## Framework Extension Points

### Custom Widget Types

#### Creating a New Widget Category

```python
class CustomAnalysisWidget(WidgetExecutor):
    """Example custom widget for specialized analysis"""
    
    def __init__(self, widget_schema):
        super().__init__(widget_schema)
        self.analysis_engine = self.initialize_analysis_engine()
    
    def _execute_impl(self, validated_input):
        analysis_type = validated_input.get('analysis_type')
        data = validated_input.get('data')
        
        result = self.analysis_engine.run_analysis(analysis_type, data)
        
        return {
            'success': True,
            'analysis_result': result,
            'metadata': {
                'analysis_type': analysis_type,
                'data_points': len(data) if data else 0,
                'execution_time': result.get('execution_time')
            }
        }
```

### Custom UI Components

#### Specialized Form Fields

```javascript
class CustomFormField {
    constructor(fieldSchema, value) {
        this.schema = fieldSchema;
        this.value = value;
        this.element = this.createElement();
    }
    
    createElement() {
        const element = document.createElement('div');
        element.className = 'custom-field';
        
        // Implement custom UI based on schema
        switch(this.schema['ui:widget']) {
            case 'matrix-input':
                return this.createMatrixInput();
            case 'color-palette':
                return this.createColorPalette();
            case 'formula-editor':
                return this.createFormulaEditor();
            default:
                return this.createDefaultInput();
        }
    }
}
```

This comprehensive architecture and examples document provides concrete implementation patterns and demonstrates the full capabilities of the widget framework. The modular design allows for extensive customization while maintaining clean interfaces and consistent behavior across all widget types.