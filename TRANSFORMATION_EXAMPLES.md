# Multi-Type Transformation Examples

This document provides concrete examples of how the proposed multi-type transformation system would work in practice.

## Example 1: Python Data Normalization (Inline)

### Arrow Configuration
```json
{
  "@context": [
    "https://www.w3.org/ns/prov-o.jsonld",
    "https://litlfred.github.io/notebooks/libraries/core/core.jsonld",
    "https://litlfred.github.io/notebooks/transformation-ontology.jsonld"
  ],
  "@id": "urn:arrow:data-source:normalizer",
  "@type": ["prov:Entity", "workflow:Connection"],
  "workflow:source": "urn:widget:data-generator",
  "workflow:target": "urn:widget:statistical-analyzer", 
  "workflow:sourceParameters": ["raw_values", "metadata"],
  "workflow:targetParameters": ["normalized_data", "stats_info"],
  "workflow:hasTransformation": {
    "@id": "urn:transform:z-score-normalization",
    "@type": ["transform:Transformation", "prov:Entity"],
    "dct:title": "Z-Score Data Normalization",
    "dct:description": "Normalizes data using z-score (standard score) method",
    "contentType": "application/x-python",
    "contentSource": "inline",
    "sourceCode": "import numpy as np\n\n# Extract values and compute statistics\nvalues = np.array(source_data['raw_values'])\nmean_val = np.mean(values)\nstd_val = np.std(values)\n\n# Z-score normalization\nnormalized = (values - mean_val) / std_val\n\n# Update source data\nsource_data['normalized_data'] = normalized.tolist()\nsource_data['stats_info'] = {\n    'original_mean': mean_val,\n    'original_std': std_val,\n    'normalized_mean': np.mean(normalized),\n    'normalized_std': np.std(normalized)\n}\n\nreturn source_data",
    "inputMapping": {
      "raw_values": "values",
      "metadata": "info"
    },
    "executionContext": {
      "@type": "transform:ExecutionContext",
      "executionTimeout": "PT30S",
      "memoryLimit": "50MB",
      "sandboxed": true,
      "allowedModules": ["numpy", "math", "statistics"]
    }
  }
}
```

### Expected JSON-LD Output
```json
{
  "@id": "urn:transform-result:z-score-normalization-20241028",
  "@type": ["transform:TransformationActivity", "prov:Activity"],
  "prov:startedAtTime": "2024-10-28T10:15:00Z",
  "prov:endedAtTime": "2024-10-28T10:15:02Z",
  "prov:used": [
    "urn:widget:data-generator",
    "urn:transform:z-score-normalization"
  ],
  "transform:executionResult": "transform:Success",
  "transform:inputData": {
    "raw_values": [1.2, 2.4, 3.1, 2.8, 4.5, 1.9, 3.7],
    "metadata": {"source": "sensor_array_01"}
  },
  "transform:outputData": {
    "normalized_data": [-1.41, -0.23, 0.31, 0.12, 1.68, -0.89, 1.02],
    "stats_info": {
      "original_mean": 2.8,
      "original_std": 1.1,
      "normalized_mean": 0.0,
      "normalized_std": 1.0
    }
  }
}
```

## Example 2: JavaScript Data Aggregation (URL Source)

### Arrow Configuration
```json
{
  "@context": [
    "https://www.w3.org/ns/prov-o.jsonld", 
    "https://litlfred.github.io/notebooks/libraries/core/core.jsonld",
    "https://litlfred.github.io/notebooks/transformation-ontology.jsonld"
  ],
  "@id": "urn:arrow:time-series:aggregator",
  "@type": ["prov:Entity", "workflow:Connection"],
  "workflow:hasTransformation": {
    "@id": "urn:transform:lodash-aggregation",
    "@type": ["transform:Transformation", "prov:Entity"],
    "dct:title": "Time Series Data Aggregation",
    "contentType": "application/javascript",
    "contentSource": "url",
    "sourceUrl": "https://transforms.example.com/time-series-aggregator.js",
    "contentHash": "sha256:a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3",
    "hashAlgorithm": "transform:SHA256",
    "dct:source": {
      "@id": "https://transforms.example.com/time-series-aggregator.js",
      "@type": ["prov:Entity", "schema:SoftwareSourceCode"],
      "schema:programmingLanguage": "javascript",
      "dct:creator": "https://orcid.org/0000-0000-0000-0001",
      "dct:license": "https://spdx.org/licenses/MIT"
    },
    "executionContext": {
      "@type": "transform:ExecutionContext",
      "executionTimeout": "PT60S",
      "memoryLimit": "100MB",
      "allowedModules": ["lodash", "moment", "d3-array"],
      "requiredCapabilities": ["array_processing", "date_manipulation"]
    }
  }
}
```

### Referenced JavaScript File Content
```javascript
// time-series-aggregator.js
const _ = require('lodash');
const moment = require('moment');

function transform_parameters(source_data, input_mapping) {
  const timeSeries = source_data.time_series_data;
  
  // Group by time intervals (hourly aggregation)
  const grouped = _.groupBy(timeSeries, (point) => {
    return moment(point.timestamp).format('YYYY-MM-DD HH:00:00');
  });
  
  // Aggregate each group
  const aggregated = _.map(grouped, (points, timeKey) => {
    return {
      timestamp: timeKey,
      count: points.length,
      sum: _.sumBy(points, 'value'),
      avg: _.meanBy(points, 'value'), 
      min: _.minBy(points, 'value').value,
      max: _.maxBy(points, 'value').value,
      std: Math.sqrt(_.sumBy(points, p => Math.pow(p.value - _.meanBy(points, 'value'), 2)) / points.length)
    };
  });
  
  source_data.aggregated_data = _.sortBy(aggregated, 'timestamp');
  source_data.aggregation_metadata = {
    interval: 'hourly',
    total_points: timeSeries.length,
    aggregated_points: aggregated.length,
    aggregation_time: new Date().toISOString()
  };
  
  return source_data;
}

// Export for Node.js execution
module.exports = { transform_parameters };
```

## Example 3: R Statistical Analysis (IRI with Semantic Context)

### Arrow Configuration
```json
{
  "@context": [
    "https://www.w3.org/ns/prov-o.jsonld",
    "https://litlfred.github.io/notebooks/libraries/core/core.jsonld", 
    "https://litlfred.github.io/notebooks/transformation-ontology.jsonld"
  ],
  "@id": "urn:arrow:dataset:statistical-analysis",
  "@type": ["prov:Entity", "workflow:Connection"],
  "workflow:hasTransformation": {
    "@id": "urn:transform:linear-regression-analysis",
    "@type": ["transform:Transformation", "prov:Entity"],
    "dct:title": "Linear Regression Statistical Analysis",
    "contentType": "application/x-r",
    "contentSource": "iri",
    "sourceUrl": "https://w3id.org/math/transforms/statistics#linear-regression-v2.1",
    "dct:source": {
      "@id": "https://w3id.org/math/transforms/statistics#linear-regression-v2.1",
      "@type": ["prov:Entity", "schema:SoftwareSourceCode", "schema:MathematicalExpression"],
      "schema:programmingLanguage": "r-lang",
      "dct:title": "Multi-variable Linear Regression with Diagnostic Plots",
      "dct:description": "Performs linear regression analysis with comprehensive diagnostics",
      "schema:version": "2.1.0",
      "dct:creator": "https://orcid.org/0000-0000-0000-0002",
      "dct:contributor": ["https://orcid.org/0000-0000-0000-0003"],
      "dct:license": "https://spdx.org/licenses/GPL-3.0",
      "schema:citation": "https://doi.org/10.1000/xyz123",
      "dct:conformsTo": "https://w3id.org/ro/terms/workflow-step"
    },
    "executionContext": {
      "@type": "transform:ExecutionContext", 
      "executionTimeout": "PT120S",
      "memoryLimit": "200MB",
      "allowedModules": ["stats", "ggplot2", "dplyr", "broom", "car"],
      "requiredCapabilities": ["statistical_modeling", "data_visualization"]
    },
    "inputMapping": {
      "dependent_var": "y",
      "independent_vars": "x_vars",
      "dataset": "data"
    }
  }
}
```

### Referenced R Script Content
```r
# Linear Regression Analysis v2.1
# Available at: https://w3id.org/math/transforms/statistics#linear-regression-v2.1

library(stats)
library(ggplot2) 
library(dplyr)
library(broom)
library(car)

transform_parameters <- function(source_data, input_mapping = NULL) {
  # Extract data
  dataset <- source_data$dataset
  y_var <- source_data$dependent_var
  x_vars <- source_data$independent_vars
  
  # Prepare formula
  formula_str <- paste(y_var, "~", paste(x_vars, collapse = " + "))
  model_formula <- as.formula(formula_str)
  
  # Fit linear model
  lm_model <- lm(model_formula, data = dataset)
  
  # Extract model statistics
  model_summary <- summary(lm_model)
  model_tidy <- tidy(lm_model)
  model_glance <- glance(lm_model)
  
  # Diagnostic tests
  residual_normality <- shapiro.test(residuals(lm_model))
  homoscedasticity <- bptest(lm_model)
  
  # Create diagnostic plots (base64 encoded)
  plot_list <- list()
  
  # Residuals vs Fitted
  png(filename = tempfile(fileext = ".png"), width = 800, height = 600)
  plot(lm_model, which = 1)
  dev.off()
  # ... additional plotting code ...
  
  # Prepare results
  source_data$regression_results <- list(
    model_summary = model_summary,
    coefficients = model_tidy,
    model_fit = model_glance,
    diagnostics = list(
      residual_normality = list(
        test = "Shapiro-Wilk",
        statistic = residual_normality$statistic,
        p_value = residual_normality$p.value,
        interpretation = ifelse(residual_normality$p.value > 0.05, "Normal", "Non-normal")
      ),
      homoscedasticity = list(
        test = "Breusch-Pagan", 
        statistic = homoscedasticity$statistic,
        p_value = homoscedasticity$p.value,
        interpretation = ifelse(homoscedasticity$p.value > 0.05, "Homoscedastic", "Heteroscedastic")
      )
    ),
    diagnostic_plots = plot_list,
    analysis_metadata = list(
      r_version = R.version.string,
      packages_used = c("stats", "ggplot2", "dplyr", "broom", "car"),
      analysis_timestamp = Sys.time()
    )
  )
  
  return(source_data)
}
```

## Example 4: SQL Data Query Transformation

### Arrow Configuration  
```json
{
  "@context": [
    "https://www.w3.org/ns/prov-o.jsonld",
    "https://litlfred.github.io/notebooks/libraries/core/core.jsonld",
    "https://litlfred.github.io/notebooks/transformation-ontology.jsonld"
  ],
  "@id": "urn:arrow:database:query-processor",
  "@type": ["prov:Entity", "workflow:Connection"],
  "workflow:hasTransformation": {
    "@id": "urn:transform:aggregation-query",
    "@type": ["transform:Transformation", "prov:Entity"],
    "dct:title": "Sales Data Aggregation Query",
    "contentType": "application/sql",
    "contentSource": "inline", 
    "sourceCode": "-- Aggregate sales data by region and product category\nSELECT \n    region,\n    product_category,\n    COUNT(*) as transaction_count,\n    SUM(amount) as total_sales,\n    AVG(amount) as average_sale,\n    MIN(amount) as min_sale,\n    MAX(amount) as max_sale,\n    STDDEV(amount) as sales_std_dev\nFROM sales_transactions \nWHERE transaction_date >= :start_date \n    AND transaction_date <= :end_date\n    AND status = 'completed'\nGROUP BY region, product_category\nORDER BY total_sales DESC",
    "executionContext": {
      "@type": "transform:ExecutionContext",
      "executionTimeout": "PT90S",
      "memoryLimit": "500MB",
      "requiredCapabilities": ["database_read"],
      "queryParameters": {
        "start_date": "2024-01-01",
        "end_date": "2024-10-31"
      }
    },
    "inputMapping": {
      "database_connection": "db_conn",
      "query_params": "params"
    }
  }
}
```

## Example 5: YAML Configuration Transformation

### Arrow Configuration
```json
{
  "@context": [
    "https://www.w3.org/ns/prov-o.jsonld",
    "https://litlfred.github.io/notebooks/libraries/core/core.jsonld",
    "https://litlfred.github.io/notebooks/transformation-ontology.jsonld"
  ],
  "@id": "urn:arrow:config-generator:deployment-manager",
  "@type": ["prov:Entity", "workflow:Connection"], 
  "workflow:hasTransformation": {
    "@id": "urn:transform:kubernetes-config-generator",
    "@type": ["transform:Transformation", "prov:Entity"],
    "dct:title": "Kubernetes Deployment Configuration Generator",
    "contentType": "application/x-yaml",
    "contentSource": "inline",
    "sourceCode": "# Generate Kubernetes deployment configuration\napiVersion: apps/v1\nkind: Deployment\nmetadata:\n  name: {{ source_data.app_name }}-deployment\n  namespace: {{ source_data.namespace | default('default') }}\n  labels:\n    app: {{ source_data.app_name }}\n    version: {{ source_data.version }}\nspec:\n  replicas: {{ source_data.replicas | default(3) }}\n  selector:\n    matchLabels:\n      app: {{ source_data.app_name }}\n  template:\n    metadata:\n      labels:\n        app: {{ source_data.app_name }}\n        version: {{ source_data.version }}\n    spec:\n      containers:\n      - name: {{ source_data.app_name }}\n        image: {{ source_data.image_registry }}/{{ source_data.app_name }}:{{ source_data.version }}\n        ports:\n        - containerPort: {{ source_data.port | default(8080) }}\n        env:\n        {% for key, value in source_data.environment_vars.items() %}\n        - name: {{ key }}\n          value: \"{{ value }}\"\n        {% endfor %}\n        resources:\n          requests:\n            memory: \"{{ source_data.memory_request | default('256Mi') }}\"\n            cpu: \"{{ source_data.cpu_request | default('100m') }}\"\n          limits:\n            memory: \"{{ source_data.memory_limit | default('512Mi') }}\"\n            cpu: \"{{ source_data.cpu_limit | default('500m') }}\"",
    "executionContext": {
      "@type": "transform:ExecutionContext",
      "executionTimeout": "PT10S",
      "memoryLimit": "10MB",
      "sandboxed": true,
      "allowedModules": ["yaml", "jinja2"],
      "templatingEngine": "jinja2"
    }
  }
}
```

## Implementation Migration Examples

### Backward Compatibility: Old vs New Format

#### Old Format (Still Supported)
```json
{
  "transformation": {
    "python_code": "source_data['result'] = source_data['x'] * 2\nreturn source_data",
    "input_mapping": {"x": "input_value"}
  }
}
```

#### New Format (Equivalent)
```json
{
  "transformation": {
    "contentType": "application/x-python",
    "contentSource": "inline", 
    "sourceCode": "source_data['result'] = source_data['x'] * 2\nreturn source_data",
    "inputMapping": {"x": "input_value"}
  }
}
```

#### Migration Function
```python
def migrate_transformation_config(old_config: Dict[str, Any]) -> Dict[str, Any]:
    """Migrate old python_code format to new multi-type format"""
    if 'python_code' in old_config:
        return {
            'contentType': 'application/x-python',
            'contentSource': 'inline',
            'sourceCode': old_config['python_code'],
            'inputMapping': old_config.get('input_mapping', {}),
            'executionContext': {
                'executionTimeout': 'PT30S',
                'memoryLimit': '50MB',
                'sandboxed': True
            }
        }
    return old_config
```

## Error Handling Examples

### Compilation Error Response
```json
{
  "@id": "urn:transform-result:compilation-error-20241028",
  "@type": ["transform:TransformationActivity", "prov:Activity"],
  "prov:startedAtTime": "2024-10-28T10:30:00Z",
  "prov:endedAtTime": "2024-10-28T10:30:01Z",
  "transform:executionResult": "transform:CompilationError",
  "transform:transformationError": "SyntaxError: invalid syntax at line 3",
  "transform:stackTrace": "File \"<transformation>\", line 3\n    source_data['result'] = source_data['x'] *\n                                             ^\nSyntaxError: invalid syntax",
  "prov:generated": {
    "@type": "transform:CompilationError",
    "dct:description": "Transformation failed to compile due to syntax error"
  }
}
```

### Runtime Error Response  
```json
{
  "@id": "urn:transform-result:runtime-error-20241028",
  "@type": ["transform:TransformationActivity", "prov:Activity"],
  "prov:startedAtTime": "2024-10-28T10:35:00Z", 
  "prov:endedAtTime": "2024-10-28T10:35:15Z",
  "transform:executionResult": "transform:RuntimeError",
  "transform:transformationError": "KeyError: 'required_field' not found in source_data",
  "transform:stackTrace": "Traceback (most recent call last):\n  File \"<transformation>\", line 5, in transform_parameters\n    value = source_data['required_field']\nKeyError: 'required_field'",
  "prov:generated": {
    "@type": "transform:RuntimeError", 
    "dct:description": "Transformation failed during execution due to missing required field"
  }
}
```

### Timeout Error Response
```json
{
  "@id": "urn:transform-result:timeout-20241028",
  "@type": ["transform:TransformationActivity", "prov:Activity"],
  "prov:startedAtTime": "2024-10-28T10:40:00Z",
  "prov:endedAtTime": "2024-10-28T10:40:30Z", 
  "transform:executionResult": "transform:Timeout",
  "transform:transformationError": "Transformation exceeded maximum execution time of 30 seconds",
  "prov:generated": {
    "@type": "transform:Timeout",
    "dct:description": "Transformation was terminated due to execution timeout"
  }
}
```

These examples demonstrate the comprehensive capabilities of the proposed multi-type transformation system, showing how it maintains backward compatibility while enabling powerful new features for multiple programming languages, external content sources, and rich semantic integration.