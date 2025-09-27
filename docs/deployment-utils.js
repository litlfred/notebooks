/**
 * Deployment Utilities for Branch-Aware GitHub Pages
 * Provides deployment context and URL generation for schema files
 * 
 * USAGE EXAMPLES:
 * 
 * // Basic deployment info
 * await window.deploymentUtils.initialize();
 * const info = window.deploymentUtils.getDeploymentInfo();
 * console.log('Deployment type:', info.deployment_type);
 * 
 * // Generate schema URLs for notebook JSON-LD
 * const context = window.deploymentUtils.getNotebookContext();
 * const widgetUrn = window.deploymentUtils.getWidgetUrn('widget-123');
 * const conformanceUrl = window.deploymentUtils.getSchemaConformanceUrl('sticky-note', 'widget');
 * 
 * // Check deployment type
 * if (window.deploymentUtils.isProduction()) {
 *     console.log('Running in production mode');
 * }
 */

class DeploymentUtils {
    constructor() {
        this.deploymentInfo = null;
        this.initialized = false;
    }
    
    /**
     * Initialize deployment context
     * @returns {Promise<Object>} Deployment context object
     */
    async initialize() {
        if (this.initialized) {
            return this.deploymentInfo;
        }
        
        try {
            // Try to load deployment info from auto-generated file
            const response = await fetch('./deployment-info.json');
            if (response.ok) {
                this.deploymentInfo = await response.json();
            } else {
                // Fallback to detecting from current URL
                this.deploymentInfo = this._detectDeploymentContext();
            }
        } catch (error) {
            console.warn('Could not load deployment info, using URL detection:', error);
            this.deploymentInfo = this._detectDeploymentContext();
        }
        
        this.initialized = true;
        console.log('Deployment context:', this.deploymentInfo);
        return this.deploymentInfo;
    }
    
    /**
     * Detect deployment context from current URL
     * @returns {Object} Deployment context
     */
    _detectDeploymentContext() {
        const currentUrl = window.location.href;
        const hostname = window.location.hostname;
        const pathname = window.location.pathname;
        
        // Check if we're on GitHub Pages
        if (hostname.includes('github.io')) {
            const pathParts = pathname.split('/').filter(p => p);
            const repo = pathParts[0] || 'notebooks';
            
            // Check if this is a branch preview
            if (pathParts.length >= 3 && pathParts[1] === 'branch-preview') {
                const branchName = pathParts[2];
                return {
                    deployment_type: 'preview',
                    branch_name: branchName,
                    base_url: `https://${hostname}/${repo}/branch-preview/${branchName}`,
                    schema_base_url: `https://${hostname}/${repo}/branch-preview/${branchName}/schema`,
                    is_production: false
                };
            } else {
                // Production deployment
                return {
                    deployment_type: 'production',
                    branch_name: 'main',
                    base_url: `https://${hostname}/${repo}`,
                    schema_base_url: `https://${hostname}/${repo}/schema`,
                    is_production: true
                };
            }
        } else {
            // Local development or other hosting
            return {
                deployment_type: 'development',
                branch_name: 'local',
                base_url: window.location.origin + pathname.replace(/\/$/, ''),
                schema_base_url: window.location.origin + pathname.replace(/\/$/, '') + '/schema',
                is_production: false
            };
        }
    }
    
    /**
     * Get the schema base URL for the current deployment
     * @returns {string} Schema base URL
     */
    getSchemaBaseUrl() {
        if (!this.initialized) {
            console.warn('DeploymentUtils not initialized. Call initialize() first.');
            return '';
        }
        return this.deploymentInfo.schema_base_url;
    }
    
    /**
     * Build a schema URL for a specific widget and file
     * @param {string} widget - Widget name (e.g., 'sticky-note', 'weierstrass')
     * @param {string} file - Schema file name (e.g., 'input.schema.json', 'widget.jsonld')
     * @returns {string} Complete schema URL
     */
    getSchemaUrl(widget, file) {
        const baseUrl = this.getSchemaBaseUrl();
        return `${baseUrl}/${widget}/${file}`;
    }
    
    /**
     * Get deployment context information
     * @returns {Object} Deployment context
     */
    getDeploymentInfo() {
        return this.deploymentInfo;
    }
    
    /**
     * Check if this is a production deployment
     * @returns {boolean} True if production deployment
     */
    isProduction() {
        return this.deploymentInfo?.is_production || false;
    }
    
    /**
     * Check if this is a preview deployment
     * @returns {boolean} True if preview deployment
     */
    isPreview() {
        return this.deploymentInfo?.deployment_type === 'preview';
    }
    
    /**
     * Get the current branch name
     * @returns {string} Branch name
     */
    getBranchName() {
        return this.deploymentInfo?.branch_name || 'unknown';
    }
    
    /**
     * Generate absolute URL for schema ontology context
     * @returns {string} Context URL for JSON-LD
     */
    getSchemaContextUrl() {
        const baseUrl = this.getSchemaBaseUrl();
        return `${baseUrl}/ontology/context.jsonld`;
    }
    
    /**
     * Generate absolute URL for a widget schema reference
     * @param {string} widget - Widget name (e.g., 'sticky-note', 'pq-torus')
     * @param {string} schemaType - Schema type ('widget', 'input', 'output')
     * @returns {string} Schema conformance URL
     */
    getSchemaConformanceUrl(widget, schemaType = 'widget') {
        const baseUrl = this.getSchemaBaseUrl();
        return `${baseUrl}/${widget}/${schemaType}.schema.json`;
    }
    
    /**
     * Generate JSON-LD context array for notebooks
     * @returns {Array<string>} Context array for JSON-LD documents
     */
    getNotebookContext() {
        return [
            "https://www.w3.org/ns/prov-o.jsonld",
            this.getSchemaContextUrl()
        ];
    }
    
    /**
     * Generate notebook URN with deployment context
     * @param {string} notebookId - Unique notebook identifier
     * @returns {string} URN for notebook
     */
    getNotebookUrn(notebookId) {
        const context = this.getDeploymentInfo();
        const branch = context?.branch_name || 'unknown';
        return `urn:notebook:${branch}:${notebookId}`;
    }
    
    /**
     * Generate widget URN with deployment context
     * @param {string} widgetId - Widget instance ID
     * @returns {string} URN for widget instance
     */
    getWidgetUrn(widgetId) {
        const context = this.getDeploymentInfo();
        const branch = context?.branch_name || 'unknown';
        return `urn:widget:${branch}:${widgetId}`;
    }
    
    /**
     * Generate activity URN for widget execution
     * @param {string} widgetId - Widget instance ID
     * @param {string} executionId - Optional execution ID
     * @returns {string} URN for activity
     */
    getActivityUrn(widgetId, executionId = null) {
        const context = this.getDeploymentInfo();
        const branch = context?.branch_name || 'unknown';
        const execId = executionId || Date.now();
        return `urn:activity:${branch}:${widgetId}:${execId}`;
    }
    
    /**
     * Generate output URN for widget results
     * @param {string} widgetId - Widget instance ID
     * @param {string} outputId - Optional output ID
     * @returns {string} URN for output entity
     */
    getOutputUrn(widgetId, outputId = null) {
        const context = this.getDeploymentInfo();
        const branch = context?.branch_name || 'unknown';
        const outId = outputId || Date.now();
        return `urn:output:${branch}:${widgetId}:${outId}`;
    }
    
    /**
     * Generate connection URN for widget connections
     * @param {string} sourceId - Source widget ID
     * @param {string} targetId - Target widget ID
     * @returns {string} URN for connection
     */
    getConnectionUrn(sourceId, targetId) {
        const context = this.getDeploymentInfo();
        const branch = context?.branch_name || 'unknown';
        return `urn:connection:${branch}:${sourceId}-${targetId}`;
    }
    
    /**
     * Display deployment info in the UI (for debugging)
     * @param {string} containerId - ID of container element
     */
    displayDeploymentInfo(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        const info = this.deploymentInfo;
        const badge = info.is_production ? 
            '<span class="badge production">PRODUCTION</span>' :
            '<span class="badge preview">PREVIEW</span>';
        
        container.innerHTML = `
            <div class="deployment-info">
                ${badge}
                <div class="deployment-details">
                    <div><strong>Branch:</strong> ${info.branch_name}</div>
                    <div><strong>Type:</strong> ${info.deployment_type}</div>
                    <div><strong>Schema Base:</strong> ${info.schema_base_url}</div>
                </div>
            </div>
        `;
    }
}

// Create global instance
window.deploymentUtils = new DeploymentUtils();

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.deploymentUtils.initialize();
    });
} else {
    window.deploymentUtils.initialize();
}

// CSS for deployment info display
const style = document.createElement('style');
style.textContent = `
.deployment-info {
    position: fixed;
    top: 10px;
    right: 10px;
    background: rgba(0,0,0,0.8);
    color: white;
    padding: 8px 12px;
    border-radius: 4px;
    font-size: 12px;
    z-index: 1000;
    font-family: monospace;
}
.deployment-info .badge {
    padding: 2px 6px;
    border-radius: 3px;
    font-weight: bold;
    margin-right: 8px;
}
.deployment-info .badge.production {
    background: #dc3545;
}
.deployment-info .badge.preview {
    background: #28a745;
}
.deployment-details {
    margin-top: 4px;
    font-size: 10px;
}
.deployment-details div {
    margin: 1px 0;
}
`;
document.head.appendChild(style);

export default DeploymentUtils;