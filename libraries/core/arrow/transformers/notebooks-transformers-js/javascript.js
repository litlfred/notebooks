/**
 * JavaScript Transformer for Notebooks
 * Handles JavaScript transformation validation and execution
 */

class JavaScriptTransformer {
    /**
     * Validate JavaScript transformation content
     * @param {string} content - The transformation code
     * @param {object} config - Transformation configuration
     * @returns {boolean} - Whether the content is valid
     */
    validate(content, config) {
        try {
            // Basic syntax validation by creating a function
            new Function('sourceData', 'inputMapping', content);
            return true;
        } catch (error) {
            console.error('JavaScript validation error:', error.message);
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
        try {
            // Apply input mapping if provided
            let mappedData = {...sourceData};
            if (inputMapping && typeof inputMapping === 'object') {
                mappedData = this.applyInputMapping(sourceData, inputMapping);
            }
            
            // Create transformation function with sourceData in scope
            const transformCode = `
                // User transformation code
                ${content}
                
                // Return the modified sourceData
                return sourceData;
            `;
            
            const transformFunction = new Function('sourceData', 'inputMapping', transformCode);
            
            // Execute transformation with timeout if specified
            const timeout = config?.executionContext?.timeout || config?.timeout || 30;
            const result = this.executeWithTimeout(transformFunction, mappedData, inputMapping, timeout * 1000);
            
            return result;
        } catch (error) {
            throw new Error(`JavaScript transformation failed: ${error.message}`);
        }
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
     * Execute transformation with timeout
     * @param {Function} func - Transformation function
     * @param {object} data - Input data
     * @param {object} mapping - Input mapping
     * @param {number} timeoutMs - Timeout in milliseconds
     * @returns {object} - Transformation result
     */
    executeWithTimeout(func, data, mapping, timeoutMs) {
        // Note: JavaScript doesn't have true timeout for synchronous code
        // This is a basic implementation that relies on the subprocess timeout
        return func(data, mapping);
    }
}

module.exports = new JavaScriptTransformer();