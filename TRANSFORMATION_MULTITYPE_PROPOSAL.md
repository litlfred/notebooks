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
        """Compile transformation based on content type using appropriate transformer"""
        content_type = self.transformation.get('content_type', 'application/x-python')
        content = self._resolve_content()
        
        # Get transformer implementation for content type
        transformer = TransformerFactory.get_transformer(content_type)
        self.transform_function = transformer.compile(content, self.transformation)
    
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

### 2. Transformer Base Class and Factory Pattern

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Callable

class BaseTransformer(ABC):
    """Base class for all transformation language implementations"""
    
    @abstractmethod
    def get_supported_mime_types(self) -> List[str]:
        """Return list of MIME types this transformer supports"""
        pass
    
    @abstractmethod
    def validate_content(self, content: str, transformation_config: Dict[str, Any]) -> bool:
        """Validate transformation content syntax and structure"""
        pass
    
    @abstractmethod
    def compile(self, content: str, transformation_config: Dict[str, Any]) -> Callable:
        """Compile transformation content into executable function"""
        pass
    
    @abstractmethod
    def execute(self, compiled_function: Callable, source_data: Dict[str, Any], 
                input_mapping: Dict[str, str] = None) -> Dict[str, Any]:
        """Execute compiled transformation function"""
        pass

class TransformerFactory:
    """Factory for managing transformer implementations"""
    
    _transformers: Dict[str, BaseTransformer] = {}
    
    @classmethod
    def register_transformer(cls, transformer: BaseTransformer):
        """Register a new transformer implementation"""
        for mime_type in transformer.get_supported_mime_types():
            cls._transformers[mime_type] = transformer
    
    @classmethod
    def get_transformer(cls, content_type: str) -> BaseTransformer:
        """Get transformer for specified content type"""
        if content_type not in cls._transformers:
            raise ValueError(f"No transformer registered for content type: {content_type}")
        return cls._transformers[content_type]
    
    @classmethod
    def list_supported_types(cls) -> List[str]:
        """List all supported MIME types"""
        return list(cls._transformers.keys())
```

### 3. Python Transformer (Built-in)

```python
class PythonTransformer(BaseTransformer):
    """Built-in Python transformation support"""
    
    def get_supported_mime_types(self) -> List[str]:
        return ['application/x-python', 'text/x-python']
    
    def validate_content(self, content: str, transformation_config: Dict[str, Any]) -> bool:
        """Validate Python syntax"""
        try:
            compile(content, '<transformation>', 'exec')
            return True
        except SyntaxError:
            return False
    
    def compile(self, content: str, transformation_config: Dict[str, Any]) -> Callable:
        """Compile Python transformation code"""
        function_code = f"""
def transform_parameters(source_data, input_mapping=None):
    '''User-defined transformation function'''
    {content}
    return source_data
"""
        local_scope = {}
        exec(function_code, {"__builtins__": __builtins__}, local_scope)
        return local_scope['transform_parameters']
    
    def execute(self, compiled_function: Callable, source_data: Dict[str, Any], 
                input_mapping: Dict[str, str] = None) -> Dict[str, Any]:
        """Execute Python transformation"""
        return compiled_function(source_data, input_mapping)

# Register built-in Python transformer
TransformerFactory.register_transformer(PythonTransformer())
```

### 4. Node.js-Based Transformer Architecture

For all non-Python languages, transformations are implemented as Node.js modules that can be imported and executed. This provides a consistent, extensible architecture for adding new languages.

#### Base Node.js Transformer Interface

```python
import subprocess
import json
import tempfile
import os
from pathlib import Path

class NodeJSTransformer(BaseTransformer):
    """Base class for Node.js-based transformers"""
    
    def __init__(self, package_name: str, module_path: str):
        self.package_name = package_name
        self.module_path = module_path
        self.node_executor = NodeExecutor()
    
    def validate_content(self, content: str, transformation_config: Dict[str, Any]) -> bool:
        """Validate content using Node.js module"""
        return self.node_executor.validate(
            self.package_name, 
            self.module_path, 
            content, 
            transformation_config
        )
    
    def compile(self, content: str, transformation_config: Dict[str, Any]) -> Callable:
        """Return a callable that will execute via Node.js"""
        def node_transformation(source_data: Dict[str, Any], input_mapping: Dict[str, str] = None):
            return self.node_executor.execute(
                self.package_name,
                self.module_path,
                content,
                source_data,
                input_mapping,
                transformation_config
            )
        return node_transformation
    
    def execute(self, compiled_function: Callable, source_data: Dict[str, Any], 
                input_mapping: Dict[str, str] = None) -> Dict[str, Any]:
        """Execute Node.js transformation"""
        return compiled_function(source_data, input_mapping)

class NodeExecutor:
    """Handles communication with Node.js transformer processes"""
    
    def __init__(self):
        self.transformers_path = Path(__file__).parent / "transformers" / "node_modules"
    
    def validate(self, package_name: str, module_path: str, content: str, 
                 config: Dict[str, Any]) -> bool:
        """Validate transformation content using Node.js module"""
        validation_script = f"""
const transformer = require('{package_name}/{module_path}');
const content = {json.dumps(content)};
const config = {json.dumps(config)};

try {{
    const isValid = transformer.validate(content, config);
    console.log(JSON.stringify({{ success: true, valid: isValid }}));
}} catch (error) {{
    console.log(JSON.stringify({{ success: false, error: error.message }}));
}}
"""
        result = self._run_node_script(validation_script)
        return result.get('success', False) and result.get('valid', False)
    
    def execute(self, package_name: str, module_path: str, content: str,
                source_data: Dict[str, Any], input_mapping: Dict[str, str],
                config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute transformation using Node.js module"""
        execution_script = f"""
const transformer = require('{package_name}/{module_path}');
const content = {json.dumps(content)};
const sourceData = {json.dumps(source_data)};
const inputMapping = {json.dumps(input_mapping)};
const config = {json.dumps(config)};

try {{
    const result = transformer.transform(content, sourceData, inputMapping, config);
    console.log(JSON.stringify({{ success: true, result: result }}));
}} catch (error) {{
    console.log(JSON.stringify({{ success: false, error: error.message, stack: error.stack }}));
}}
"""
        result = self._run_node_script(execution_script)
        if result.get('success', False):
            return result.get('result', source_data)
        else:
            raise RuntimeError(f"Node.js transformation failed: {result.get('error', 'Unknown error')}")
    
    def _run_node_script(self, script: str) -> Dict[str, Any]:
        """Execute Node.js script and return parsed JSON result"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(script)
            script_path = f.name
        
        try:
            # Execute Node.js script with proper PATH and timeout
            result = subprocess.run(
                ['node', script_path],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.transformers_path
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout.strip())
            else:
                return {"success": False, "error": result.stderr}
                
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Transformation timed out"}
        except json.JSONDecodeError:
            return {"success": False, "error": "Invalid JSON response from Node.js"}
        finally:
            os.unlink(script_path)
```

### 5. Language-Specific Transformer Implementations

#### JavaScript Transformer
```python
class JavaScriptTransformer(NodeJSTransformer):
    """JavaScript/Node.js transformation support"""
    
    def __init__(self):
        super().__init__('notebooks-transformers-js', 'javascript')
    
    def get_supported_mime_types(self) -> List[str]:
        return ['application/javascript', 'text/javascript']

# Register JavaScript transformer
TransformerFactory.register_transformer(JavaScriptTransformer())
```

#### R Transformer
```python
class RTransformer(NodeJSTransformer):
    """R transformation support via Node.js R interface"""
    
    def __init__(self):
        super().__init__('notebooks-transformers-r', 'r-lang')
    
    def get_supported_mime_types(self) -> List[str]:
        return ['application/x-r', 'text/x-r']

# Register R transformer
TransformerFactory.register_transformer(RTransformer())
```

#### SQL Transformer
```python
class SQLTransformer(NodeJSTransformer):
    """SQL transformation support"""
    
    def __init__(self):
        super().__init__('notebooks-transformers-sql', 'sql')
    
    def get_supported_mime_types(self) -> List[str]:
        return ['application/sql', 'text/sql']

# Register SQL transformer
TransformerFactory.register_transformer(SQLTransformer())
```

### 6. Node.js Transformer Package Structure

Each language transformer is implemented as a Node.js package following a standard interface:

#### Package Structure
```
transformers/
├── package.json
├── node_modules/
│   ├── notebooks-transformers-js/
│   │   ├── package.json
│   │   ├── javascript.js
│   │   └── index.js
│   ├── notebooks-transformers-r/
│   │   ├── package.json
│   │   ├── r-lang.js
│   │   └── index.js
│   └── notebooks-transformers-sql/
│       ├── package.json
│       ├── sql.js
│       └── index.js
```

#### Standard Transformer Interface (Node.js)
Each transformer package must implement this interface:

```javascript
// notebooks-transformers-js/javascript.js
class JavaScriptTransformer {
    /**
     * Validate JavaScript transformation content
     * @param {string} content - The transformation code
     * @param {object} config - Transformation configuration
     * @returns {boolean} - Whether the content is valid
     */
    validate(content, config) {
        try {
            // Basic syntax validation
            new Function(content);
            return true;
        } catch (error) {
            return false;
        }
    }
    
    /**
     * Execute JavaScript transformation
     * @param {string} content - The transformation code
     * @param {object} sourceData - Input data from source widget
     * @param {object} inputMapping - Parameter mapping configuration
     * @param {object} config - Transformation execution context
     * @returns {object} - Transformed data
     */
    transform(content, sourceData, inputMapping, config) {
        // Create transformation function
        const transformFunction = new Function('sourceData', 'inputMapping', content + '\nreturn sourceData;');
        
        // Apply input mapping if provided
        let mappedData = sourceData;
        if (inputMapping) {
            mappedData = this.applyInputMapping(sourceData, inputMapping);
        }
        
        // Execute transformation with security context
        const result = this.executeInSandbox(transformFunction, mappedData, inputMapping, config);
        
        return result;
    }
    
    /**
     * Apply input parameter mapping
     * @param {object} data - Source data
     * @param {object} mapping - Parameter mapping
     * @returns {object} - Mapped data
     */
    applyInputMapping(data, mapping) {
        const mapped = {...data};
        for (const [source, target] of Object.entries(mapping)) {
            if (source in data) {
                mapped[target] = data[source];
            }
        }
        return mapped;
    }
    
    /**
     * Execute transformation in sandboxed environment
     * @param {Function} func - Transformation function
     * @param {object} data - Input data
     * @param {object} mapping - Input mapping
     * @param {object} config - Execution configuration
     * @returns {object} - Transformation result
     */
    executeInSandbox(func, data, mapping, config) {
        // Set up execution timeout
        const timeout = config.executionContext?.timeout || 30;
        
        return new Promise((resolve, reject) => {
            const timer = setTimeout(() => {
                reject(new Error(`Transformation timed out after ${timeout} seconds`));
            }, timeout * 1000);
            
            try {
                const result = func(data, mapping);
                clearTimeout(timer);
                resolve(result);
            } catch (error) {
                clearTimeout(timer);
                reject(error);
            }
        });
    }
}

module.exports = new JavaScriptTransformer();
```

#### R Transformer Example
```javascript
// notebooks-transformers-r/r-lang.js
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

class RTransformer {
    validate(content, config) {
        try {
            // Create temporary R script to validate syntax
            const tempScript = this.createTempScript(content);
            execSync(`Rscript --vanilla -e "source('${tempScript}')"`, { timeout: 5000 });
            fs.unlinkSync(tempScript);
            return true;
        } catch (error) {
            return false;
        }
    }
    
    transform(content, sourceData, inputMapping, config) {
        const tempScript = this.createTransformScript(content, sourceData, inputMapping);
        
        try {
            const result = execSync(`Rscript --vanilla ${tempScript}`, { 
                timeout: (config.executionContext?.timeout || 60) * 1000,
                encoding: 'utf8'
            });
            
            // Parse JSON result from R script
            const transformedData = JSON.parse(result);
            fs.unlinkSync(tempScript);
            
            return transformedData;
        } catch (error) {
            fs.unlinkSync(tempScript);
            throw error;
        }
    }
    
    createTransformScript(content, sourceData, inputMapping) {
        const rScript = `
library(jsonlite)

# Load source data
source_data <- fromJSON('${JSON.stringify(sourceData)}')
input_mapping <- fromJSON('${JSON.stringify(inputMapping || {})}')

# User transformation code
${content}

# Output result as JSON
cat(toJSON(source_data, auto_unbox = TRUE))
`;
        
        const tempPath = path.join(__dirname, `temp_${Date.now()}.R`);
        fs.writeFileSync(tempPath, rScript);
        return tempPath;
    }
    
    createTempScript(content) {
        const tempPath = path.join(__dirname, `validate_${Date.now()}.R`);
        fs.writeFileSync(tempPath, content);
        return tempPath;
    }
}

module.exports = new RTransformer();
```

### 7. Adding New Language Support

Adding support for a new transformation language is straightforward:

#### Step 1: Create Node.js Package
```bash
mkdir transformers/node_modules/notebooks-transformers-{language}
cd transformers/node_modules/notebooks-transformers-{language}
npm init -y
```

#### Step 2: Implement Transformer Interface
```javascript
// {language}.js
class NewLanguageTransformer {
    validate(content, config) {
        // Implement language-specific validation
        return true;
    }
    
    transform(content, sourceData, inputMapping, config) {
        // Implement language-specific transformation
        return sourceData;
    }
}

module.exports = new NewLanguageTransformer();
```

#### Step 3: Register Python Wrapper
```python
class NewLanguageTransformer(NodeJSTransformer):
    def __init__(self):
        super().__init__('notebooks-transformers-{language}', '{language}')
    
    def get_supported_mime_types(self) -> List[str]:
        return ['application/x-{language}', 'text/x-{language}']

# Register the new transformer
TransformerFactory.register_transformer(NewLanguageTransformer())
```

#### Step 4: Update MIME Type Registry
Add the new MIME types to the enhanced arrow input schema and JSON-LD context definitions.

This architecture provides:
- **Consistent Interface**: All transformers follow the same pattern
- **Easy Extension**: New languages require minimal boilerplate
- **Isolation**: Each language runs in its own Node.js context
- **Validation**: Built-in content validation before execution
- **Security**: Configurable timeouts and sandboxing
- **Maintainability**: Clear separation between Python orchestration and language-specific logic

### 8. Content Resolution System

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
- Set up Node.js transformer execution environment
- Install base transformer packages (JavaScript, R, SQL)
- Implement NodeJSTransformer base class and factory system
- Add validation and execution interfaces for each language

### Phase 3: Advanced Features
- IRI resolution with semantic web context
- Transformation composition and chaining
- Performance optimization and caching
- Additional language transformers via npm packages

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

### Example 1: Python Data Normalization (Built-in)
```json
{
  "transformation": {
    "content_type": "application/x-python",
    "content_source": "inline",
    "content": "import numpy as np\nsource_data['normalized'] = (source_data['values'] - np.mean(source_data['values'])) / np.std(source_data['values'])\nreturn source_data",
    "execution_context": {
      "timeout": 30,
      "memory_limit": "50MB",
      "allowed_modules": ["numpy", "math", "statistics"]
    }
  }
}
```

### Example 2: JavaScript Data Transformation (Node.js Module)
```json
{
  "transformation": {
    "content_type": "application/javascript",
    "content_source": "inline",
    "content": "// Use lodash for data manipulation\nconst _ = require('lodash');\n\n// Group and aggregate data\nconst grouped = _.groupBy(sourceData.timeSeries, 'category');\nsourceData.aggregated = _.mapValues(grouped, (items) => ({\n  count: items.length,\n  sum: _.sumBy(items, 'value'),\n  avg: _.meanBy(items, 'value')\n}));\n\nreturn sourceData;",
    "execution_context": {
      "timeout": 60,
      "memory_limit": "100MB",
      "allowed_modules": ["lodash", "moment", "d3-array"]
    }
  }
}
```

### Example 3: R Statistical Analysis (Node.js-R Bridge)
```json
{
  "transformation": {
    "content_type": "application/x-r",
    "content_source": "inline", 
    "content": "library(stats)\nlibrary(dplyr)\n\n# Perform linear regression\nmodel <- lm(y ~ x1 + x2, data = source_data$dataset)\n\n# Add fitted values and residuals\nsource_data$dataset$fitted <- fitted(model)\nsource_data$dataset$residuals <- residuals(model)\n\n# Model summary\nsource_data$model_summary <- list(\n  r_squared = summary(model)$r.squared,\n  coefficients = summary(model)$coefficients,\n  p_value = summary(model)$fstatistic\n)",
    "execution_context": {
      "timeout": 120,
      "memory_limit": "200MB",
      "allowed_modules": ["stats", "dplyr", "ggplot2"]
    }
  }
}
```

### Example 4: SQL Query Transformation (Node.js-SQL Engine)
```json
{
  "transformation": {
    "content_type": "application/sql",
    "content_source": "inline",
    "content": "SELECT region, product_category, COUNT(*) as transaction_count, SUM(amount) as total_sales, AVG(amount) as avg_sale FROM transactions WHERE date >= :start_date AND date <= :end_date GROUP BY region, product_category ORDER BY total_sales DESC",
    "execution_context": {
      "timeout": 90,
      "memory_limit": "500MB",
      "required_capabilities": ["database_read"],
      "query_parameters": {
        "start_date": "2024-01-01",
        "end_date": "2024-12-31"
      }
    }
  }
}
```

### Example 5: Custom Language Transformer Package
```json
{
  "transformation": {
    "content_type": "application/x-julia",
    "content_source": "url",
    "source_url": "https://transforms.example.com/numerical-analysis.jl",
    "execution_context": {
      "timeout": 180,
      "memory_limit": "1GB",
      "package_name": "notebooks-transformers-julia",
      "module_path": "julia-lang"
    }
  }
}
```

#### Adding Julia Support (Example)
```javascript
// transformers/node_modules/notebooks-transformers-julia/julia-lang.js
const { execSync } = require('child_process');

class JuliaTransformer {
    validate(content, config) {
        try {
            execSync(`julia -e "include_string(Main, ${JSON.stringify(content)})"`, { timeout: 5000 });
            return true;
        } catch (error) {
            return false;
        }
    }
    
    transform(content, sourceData, inputMapping, config) {
        const juliaScript = `
using JSON

# Load source data  
source_data = JSON.parse("""${JSON.stringify(sourceData)}""")
input_mapping = JSON.parse("""${JSON.stringify(inputMapping || {})}""")

# User transformation code
${content}

# Output result
println(JSON.json(source_data))
`;
        
        const result = execSync(`julia -e '${juliaScript}'`, {
            timeout: (config.executionContext?.timeout || 120) * 1000,
            encoding: 'utf8'
        });
        
        return JSON.parse(result.trim());
    }
}

module.exports = new JuliaTransformer();
```

```python
# Python wrapper for Julia transformer
class JuliaTransformer(NodeJSTransformer):
    def __init__(self):
        super().__init__('notebooks-transformers-julia', 'julia-lang')
    
    def get_supported_mime_types(self) -> List[str]:
        return ['application/x-julia', 'text/x-julia']

# Register automatically
TransformerFactory.register_transformer(JuliaTransformer())
```
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