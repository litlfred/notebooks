# Multi-Type Transformation Proposal

## Executive Summary

This proposal outlines how to extend the current arrow transformation system from Python-only to support multiple transformation languages using MIME types, while providing flexible content sourcing options including inline content, URLs, and JSON-LD compatible IRIs.

## Current System Analysis

### Existing Implementation

The current arrow transformation system in `libraries/core/arrow/arrow.py` supports:

```python
class WorkflowArrow:
    def __init__(self, arrow_config: Dict[str, Any]):
        self.transformation = arrow_config.get('transformation', {})
        if 'python_code' in self.transformation:
            self._compile_transformation()
    
    def _compile_transformation(self):
        python_code = self.transformation['python_code']
        # Direct exec() execution of Python code
```

**Current JSON Schema** (`libraries/core/arrow/input.schema.json`):
```json
{
  "transformation": {
    "type": "object",
    "properties": {
      "python_code": {
        "type": "string",
        "description": "Optional Python function body for ETL transformation"
      },
      "input_mapping": {
        "type": "object",
        "description": "Optional parameter name mapping"
      }
    }
  }
}
```

### Limitations of Current Approach

1. **Single Language**: Only Python supported via hardcoded `python_code` field
2. **Inline Only**: No support for external script references
3. **Limited Extensibility**: Adding new languages requires schema changes
4. **No Semantic Context**: Missing JSON-LD vocabulary for transformations

## Proposed Solution: Multi-Type Transformations

### 1. Enhanced Schema Structure

**New Transformation Object**:
```json
{
  "transformation": {
    "content_type": "application/x-python",
    "content": "source_data['x'] = source_data['x'] * 2\nreturn source_data",
    "source": "inline",
    "url": null,
    "input_mapping": {"p": "prime_p", "q": "prime_q"},
    "execution_context": {
      "timeout": 30,
      "memory_limit": "100MB",
      "sandbox": true
    }
  }
}
```

### 2. MIME Type Support Strategy

#### Core Language Support
- **Python**: `application/x-python`, `text/x-python`
- **JavaScript/Node.js**: `application/javascript`, `text/javascript`
- **R**: `application/x-r`, `text/x-r`
- **SQL**: `application/sql`, `text/sql`
- **Shell/Bash**: `application/x-sh`, `text/x-shellscript`

#### Configuration & Data Languages
- **YAML**: `application/x-yaml`, `text/yaml`
- **TOML**: `application/toml`, `text/toml`
- **JSON**: `application/json` (for data transformations)

#### Custom Domain-Specific Languages
- **Mathematical DSL**: `application/x-math-expression`
- **Custom Widget Language**: `application/x-widget-transform`

### 3. Content Source Options

#### Inline Content
```json
{
  "transformation": {
    "content_type": "application/x-python",
    "source": "inline",
    "content": "# Direct Python code here\nresult = source_data['x'] * 2"
  }
}
```

#### URL References
```json
{
  "transformation": {
    "content_type": "application/javascript",
    "source": "url",
    "url": "https://example.com/transforms/data-processor.js",
    "content": null
  }
}
```

#### IRI with JSON-LD Context
```json
{
  "transformation": {
    "content_type": "application/x-r",
    "source": "iri",
    "url": "https://w3id.org/transforms/statistical-analysis#regression",
    "dct:source": {
      "@id": "https://w3id.org/transforms/statistical-analysis#regression",
      "@type": ["prov:Entity", "schema:SoftwareSourceCode"],
      "schema:programmingLanguage": "R",
      "prov:wasAttributedTo": "https://orcid.org/0000-0000-0000-0000"
    }
  }
}
```

### 4. JSON-LD Integration

#### Enhanced JSON-LD Context
```json
{
  "@context": {
    "workflow": "https://litlfred.github.io/notebooks/ontology/workflow#",
    "transform": "https://litlfred.github.io/notebooks/ontology/transform#",
    "dct": "http://purl.org/dc/terms/",
    "schema": "https://schema.org/",
    "prov": "https://www.w3.org/ns/prov#",
    
    "Transformation": "transform:Transformation",
    "contentType": {"@id": "dct:format", "@type": "@id"},
    "sourceCode": {"@id": "schema:sourceCode", "@type": "xsd:string"},
    "programmingLanguage": {"@id": "schema:programmingLanguage", "@type": "@id"}
  }
}
```

#### Complete JSON-LD Example
```json
{
  "@id": "urn:arrow:widget1:widget2",
  "@type": ["prov:Entity", "workflow:Connection"],
  "workflow:hasTransformation": {
    "@id": "urn:transform:data-normalizer",
    "@type": ["prov:Entity", "transform:Transformation"],
    "dct:format": "application/x-python",
    "schema:sourceCode": "# Normalize data\nresult = (source_data - mean) / std",
    "schema:programmingLanguage": "Python",
    "transform:executionContext": {
      "transform:timeout": "PT30S",
      "transform:memoryLimit": "100MB",
      "transform:sandboxed": true
    },
    "prov:wasGeneratedBy": {
      "@type": "prov:Activity",
      "prov:startedAtTime": "2024-09-28T10:00:00Z"
    }
  }
}
```

## Implementation Architecture

### 1. Enhanced Arrow Class Structure

```python
class WorkflowArrow:
    def __init__(self, arrow_config: Dict[str, Any]):
        self.transformation = arrow_config.get('transformation', {})
        self.transform_function = None
        
        if self.transformation:
            self._compile_transformation()
    
    def _compile_transformation(self):
        """Compile transformation based on content type"""
        content_type = self.transformation.get('content_type', 'application/x-python')
        content = self._resolve_content()
        
        # Dispatch to appropriate compiler
        if content_type in ['application/x-python', 'text/x-python']:
            self.transform_function = self._compile_python(content)
        elif content_type in ['application/javascript', 'text/javascript']:
            self.transform_function = self._compile_javascript(content)
        elif content_type in ['application/x-r', 'text/x-r']:
            self.transform_function = self._compile_r(content)
        else:
            raise ValueError(f"Unsupported content type: {content_type}")
    
    def _resolve_content(self) -> str:
        """Resolve content from inline, URL, or IRI source"""
        source_type = self.transformation.get('source', 'inline')
        
        if source_type == 'inline':
            return self.transformation.get('content', '')
        elif source_type in ['url', 'iri']:
            url = self.transformation.get('url')
            return self._fetch_content(url)
        else:
            raise ValueError(f"Unsupported source type: {source_type}")
    
    def _fetch_content(self, url: str) -> str:
        """Fetch content from URL with proper caching and security"""
        # Implementation details for URL resolution
        pass
```

### 2. Language-Specific Compilers

```python
def _compile_python(self, code: str) -> Callable:
    """Compile Python transformation code"""
    function_code = f"""
def transform_parameters(source_data, input_mapping=None):
    '''User-defined transformation function'''
    {code}
    return source_data
"""
    local_scope = {}
    exec(function_code, {"__builtins__": __builtins__}, local_scope)
    return local_scope['transform_parameters']

def _compile_javascript(self, code: str) -> Callable:
    """Compile JavaScript transformation using embedded V8 or similar"""
    # Could use PyV8, js2py, or subprocess to Node.js
    pass

def _compile_r(self, code: str) -> Callable:
    """Compile R transformation using rpy2 or subprocess"""
    # Implementation using rpy2 or R subprocess execution
    pass
```

### 3. Content Resolution System

```python
class ContentResolver:
    def __init__(self):
        self.cache = {}
        self.allowed_domains = set()
        self.security_policies = {}
    
    def resolve(self, source_type: str, url: str = None, content: str = None) -> str:
        """Resolve content with caching and security checks"""
        if source_type == 'inline':
            return content or ''
        
        elif source_type in ['url', 'iri']:
            return self._fetch_with_cache(url)
    
    def _fetch_with_cache(self, url: str) -> str:
        """Fetch URL content with proper caching"""
        if url in self.cache:
            return self.cache[url]
        
        # Security validation
        self._validate_url(url)
        
        # Fetch content
        content = self._safe_fetch(url)
        self.cache[url] = content
        return content
```

## Migration Strategy

### Phase 1: Backward Compatibility
- Support both old `python_code` and new `content_type` fields
- Default `content_type` to `application/x-python` when missing
- Automatic migration of existing configurations

### Phase 2: Extended Language Support
- Add JavaScript/Node.js execution environment
- Implement R transformation support
- Add SQL query transformations

### Phase 3: Advanced Features
- IRI resolution with semantic web context
- Transformation composition and chaining
- Performance optimization and caching

## Security Considerations

### 1. Content Source Validation
- **URL Allowlisting**: Only allowed domains for external content
- **Content Integrity**: SHA-256 hashes for external scripts
- **Rate Limiting**: Prevent abuse of external URL fetching

### 2. Execution Sandboxing
- **Resource Limits**: Memory, CPU, and time constraints
- **Network Isolation**: Restrict network access from transformations
- **File System Access**: Limited or no file system access

### 3. Code Validation
- **Static Analysis**: Basic syntax checking before execution
- **Capability Restrictions**: Limit available functions and modules
- **Audit Logging**: Track all transformation executions

## Examples

### Example 1: Python Data Normalization
```json
{
  "transformation": {
    "content_type": "application/x-python",
    "source": "inline",
    "content": "import numpy as np\nsource_data['normalized'] = (source_data['values'] - np.mean(source_data['values'])) / np.std(source_data['values'])\nreturn source_data"
  }
}
```

### Example 2: JavaScript Data Transformation
```json
{
  "transformation": {
    "content_type": "application/javascript",
    "source": "url",
    "url": "https://transforms.example.com/lodash-data-processor.js",
    "execution_context": {
      "timeout": 10,
      "modules": ["lodash", "moment"]
    }
  }
}
```

### Example 3: R Statistical Analysis
```json
{
  "transformation": {
    "content_type": "application/x-r",
    "source": "inline",
    "content": "result <- lm(y ~ x, data=source_data)\nsource_data$fitted <- fitted(result)\nsource_data",
    "execution_context": {
      "packages": ["stats", "dplyr"]
    }
  }
}
```

### Example 4: JSON-LD Semantic Transformation
```json
{
  "@context": [
    "https://www.w3.org/ns/prov-o.jsonld",
    "https://litlfred.github.io/notebooks/libraries/core/core.jsonld"
  ],
  "@id": "urn:arrow:source:target",
  "@type": ["prov:Entity", "workflow:Connection"],
  "workflow:hasTransformation": {
    "@id": "urn:transform:semantic-mapper",
    "@type": ["transform:Transformation", "prov:Entity"],
    "dct:format": "application/x-python",
    "dct:source": {
      "@id": "https://w3id.org/math/transforms#coordinate-transform",
      "@type": "schema:SoftwareSourceCode",
      "schema:programmingLanguage": "Python",
      "dct:title": "Coordinate System Transformation",
      "dct:creator": "https://orcid.org/0000-0000-0000-0000"
    },
    "schema:sourceCode": "# Convert from Cartesian to polar coordinates\nimport math\nr = math.sqrt(source_data['x']**2 + source_data['y']**2)\ntheta = math.atan2(source_data['y'], source_data['x'])\nsource_data.update({'r': r, 'theta': theta})\nreturn source_data"
  }
}
```

## Standards Compliance

### MIME Type Standards
- Follow RFC 6838 for MIME type registration
- Use `application/x-*` for experimental language types
- Register custom types through proper channels

### JSON-LD Best Practices
- Use established vocabularies (PROV-O, Schema.org, Dublin Core)
- Provide clear context definitions
- Enable semantic reasoning and validation

### Web Standards Alignment
- Compatible with W3C standards for web semantics
- Follows REST principles for URL-based content
- Supports standard HTTP caching headers

## Conclusion

This proposal provides a comprehensive path for extending the transformation system to support multiple languages while maintaining backward compatibility and adding powerful new capabilities for content sourcing and semantic integration. The MIME type approach ensures standards compliance and extensibility, while the JSON-LD integration enables rich semantic context and provenance tracking.

The phased implementation approach allows for gradual rollout and testing, ensuring system stability while adding significant new capabilities to the widget framework.