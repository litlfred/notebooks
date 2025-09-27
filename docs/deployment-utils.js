/**
 * Deployment Utilities for Branch-Aware GitHub Pages
 * Provides deployment context and URL generation for schema files
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