# Multi-Action Widget Interface Specification

## Overview

This document specifies the multi-action widget interface that enables widgets to define multiple named actions with different output formats, JSON schema validation, localized names, and hierarchical menus.

## Core Features

### 1. JSON Schema Validation

All widget actions validate input data against the widget's input schema before execution:

- **Required by default**: Actions validate input unless explicitly disabled
- **Type checking**: Integer, number, string, boolean validation
- **Range validation**: Minimum/maximum constraints for numeric values
- **Required field validation**: Ensures all required properties are present

```python
def validate_input_for_action(self, input_data: Dict[str, Any], action_slug: str) -> Dict[str, Any]:
    """Validate input data against schema for a specific action"""
    action_config = self.actions.get(action_slug, {})
    validation_required = action_config.get('validation_required', True)
    
    if not validation_required:
        return input_data
        
    return self.validate_input(input_data)
```

### 2. Multiple Named Actions per Widget

Each widget can define multiple actions with different purposes:

```json
{
  "actions": {
    "render-markdown": {
      "slug": "render-markdown",
      "names": {
        "en": "Render Markdown",
        "es": "Renderizar Markdown"
      },
      "icon": "📝",
      "output_format": "html"
    },
    "export-pdf": {
      "slug": "export-pdf", 
      "names": {
        "en": "Export PDF"
      },
      "icon": "📄",
      "output_format": "pdf"
    }
  }
}
```

### 3. Action Schema Structure

Each action must follow this schema:

- **slug**: `^[a-z]+(-[a-z]+)*$` pattern (lowercase letters and dashes)
- **names**: Object with locale keys (`en`, `es`, `fr`, `de`, etc.)
- **icon**: Emoji or icon identifier (max 10 characters)
- **description**: Localized descriptions object
- **menu_category**: Hierarchical category for hamburger menu
- **output_format**: One of `json`, `html`, `svg`, `png`, `pdf`, `markdown`
- **validation_required**: Boolean (default: true)

### 4. Common Input/Output Schema

All actions within a widget share the same input and output schema:

- **Input Schema**: Validated before any action execution
- **Output Schema**: Consistent structure across all actions
- **Schema Precedence**: First schema in array takes precedence

### 5. Localized Human Names

Actions support internationalization:

```json
{
  "names": {
    "en": "Render Markdown",
    "en-US": "Render Markdown Document",
    "es": "Renderizar Markdown", 
    "fr": "Rendre Markdown",
    "de": "Markdown Rendern"
  }
}
```

**Supported Locales:**
- English: `en`, `en-US`
- Spanish: `es`
- French: `fr` 
- German: `de`

### 6. Icons and Visual Identity

Each action has an associated icon/emoji:

- **Widget Icons**: Used in hamburger menu
- **Action Icons**: Specific to each action
- **Visual Consistency**: Icons reflect action purpose

### 7. Hierarchical Hamburger Menu

Actions are organized into categories in the widget hamburger menu:

**Menu Categories:**
- `display`: Rendering and visualization actions
- `export`: Export and download actions
- `computation`: Mathematical and analytical actions
- `analysis`: Data analysis and processing actions
- `actions`: Default category for uncategorized actions

### 8. Output Formats

Actions can generate different output formats:

#### HTML Format (`html`)
```json
{
  "rendered_html": "<div class='action-result'>...</div>",
  "output_format": "html"
}
```

#### SVG Format (`svg`)
```json
{
  "svg_content": "<svg>...</svg>",
  "output_format": "svg"
}
```

#### PNG Format (`png`)
```json
{
  "image_data": {
    "base64": "data:image/png;base64,...",
    "width": 200,
    "height": 100
  }
}
```

#### PDF Format (`pdf`)
```json
{
  "pdf_data": {
    "size": "2.3KB",
    "pages": 1,
    "download_url": "#pdf-download"
  }
}
```

#### Markdown Format (`markdown`)
```json
{
  "markdown_content": "# Result\n\nAction completed successfully."
}
```

## Implementation Examples

### Sticky Note Widget Actions

```json
{
  "actions": {
    "render-markdown": {
      "slug": "render-markdown",
      "names": {"en": "Render Markdown"},
      "icon": "📝",
      "menu_category": "display",
      "output_format": "html"
    },
    "export-pdf": {
      "slug": "export-pdf",
      "names": {"en": "Export PDF"},
      "icon": "📄", 
      "menu_category": "export",
      "output_format": "pdf"
    }
  }
}
```

### PQ-Torus Widget Actions

```json
{
  "actions": {
    "compute-lattice": {
      "slug": "compute-lattice",
      "names": {"en": "Compute Lattice"},
      "icon": "🔢",
      "menu_category": "computation",
      "output_format": "json"
    },
    "export-latex": {
      "slug": "export-latex",
      "names": {"en": "Export LaTeX"},
      "icon": "📐",
      "menu_category": "export", 
      "output_format": "markdown"
    }
  }
}
```

### Weierstrass Visualization Actions

```json
{
  "actions": {
    "render-png": {
      "slug": "render-png",
      "names": {"en": "Render PNG"},
      "icon": "🖼️",
      "menu_category": "render",
      "output_format": "png"
    },
    "render-svg": {
      "slug": "render-svg", 
      "names": {"en": "Render SVG"},
      "icon": "📐",
      "menu_category": "render",
      "output_format": "svg"
    }
  }
}
```

## JavaScript Interface

### Action Execution

```javascript
async function executeWidgetAction(widgetId, actionSlug) {
    await boardApp.executeWidgetAction(widgetId, actionSlug);
    // Close hamburger menu
    document.getElementById(`menu-${widgetId}`).style.display = 'none';
}
```

### Menu Toggle

```javascript
function toggleWidgetMenu(widgetId) {
    const menu = document.getElementById(`menu-${widgetId}`);
    menu.style.display = menu.style.display === 'none' ? 'block' : 'none';
    
    // Close other menus
    document.querySelectorAll('.hamburger-dropdown').forEach(dropdown => {
        if (dropdown.id !== `menu-${widgetId}`) {
            dropdown.style.display = 'none';
        }
    });
}
```

## Python Backend Integration

### Action Execution

```python
class WidgetExecutor:
    def execute_action(self, input_data: Dict[str, Any], action_slug: str) -> Dict[str, Any]:
        """Execute specific widget action with validation"""
        if action_slug not in self.actions:
            raise ValueError(f"Action '{action_slug}' not found")
        
        action_config = self.actions[action_slug]
        validated_input = self.validate_input_for_action(input_data, action_slug)
        
        result = self._execute_action_impl(validated_input, action_slug, action_config)
        result.update({
            'action_slug': action_slug,
            'output_format': action_config.get('output_format', 'json'),
            'success': True
        })
        return result
```

### Action Menu Generation

```python
def get_action_menu(self, locale: str = 'en') -> Dict[str, Any]:
    """Get hierarchical action menu for widget interface"""
    menu = {}
    
    for action_slug, action_config in self.actions.items():
        category = action_config.get('menu_category', 'actions')
        action_name = action_config.get('names', {}).get(locale, action_slug)
        
        if category not in menu:
            menu[category] = []
        
        menu[category].append({
            'slug': action_slug,
            'name': action_name,
            'icon': action_config.get('icon', '⚙️')
        })
    
    return menu
```

## Migration Path

### Existing Widgets

1. **Add actions property** to widget schema
2. **Define default action** that matches current behavior  
3. **Add export/render variations** as additional actions
4. **Maintain backward compatibility** with single execute() method

### Schema Updates

1. **Update widget schemas** to include actions definitions
2. **Add validation patterns** for action slugs
3. **Include localization support** for names and descriptions
4. **Define output format enums** for type safety

## Best Practices

### Action Design

- **Descriptive names**: Use clear, action-oriented names
- **Consistent icons**: Use appropriate emojis/icons for actions
- **Logical categories**: Group related actions together
- **Output formats**: Match format to action purpose

### Validation Strategy

- **Enable by default**: Most actions should validate input
- **Disable selectively**: Only for actions that don't need validation
- **Comprehensive checking**: Validate types, ranges, required fields
- **Clear error messages**: Provide helpful validation feedback

### Internationalization

- **English required**: Always provide English names
- **Locale fallback**: Fall back to English if locale not available
- **Consistent terminology**: Use consistent terms across actions
- **Cultural adaptation**: Consider cultural context in naming

### Performance Considerations

- **Lazy loading**: Load action menus on demand
- **Validation caching**: Cache validation results where appropriate
- **Format optimization**: Optimize output formats for size/quality
- **Memory management**: Clean up large outputs after use

## Testing Strategy

### Unit Tests

- **Schema validation**: Test all validation scenarios
- **Action execution**: Test each action type  
- **Error handling**: Test validation failures
- **Localization**: Test all supported locales

### Integration Tests

- **Menu rendering**: Test hamburger menu generation
- **Action triggering**: Test UI action execution
- **Output formatting**: Test all output formats
- **Widget communication**: Test action results in workflows

### User Experience Tests

- **Menu usability**: Test hierarchical menu navigation
- **Action discovery**: Test action discoverability
- **Localization**: Test with different locale settings  
- **Performance**: Test with many actions per widget

This multi-action interface provides a flexible, extensible foundation for widget functionality while maintaining consistency and usability across the platform.