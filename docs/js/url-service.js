/**
 * URL Service for Frontend
 * Provides environment-aware URL generation for JavaScript components
 */

class URLService {
    constructor() {
        this.config = null;
        this.baseUrl = null;
        this.deploymentType = null;
        
        // Initialize from deployment config
        this.initializeFromConfig();
    }
    
    /**
     * Initialize URL service from deployment configuration
     */
    async initializeFromConfig() {
        try {
            // Try to load deployment config
            const configResponse = await fetch('./deployment-config.json');
            if (configResponse.ok) {
                this.config = await configResponse.json();
                this.baseUrl = this.config.baseUrl;
                this.deploymentType = this.config.deploymentType;
                console.log('📐 URL Service initialized:', this.config);
            } else {
                throw new Error('Config not found');
            }
        } catch (error) {
            // Fallback to detecting from current URL
            this.initializeFromCurrentURL();
        }
    }
    
    /**
     * Fallback initialization from current URL
     */
    initializeFromCurrentURL() {
        const currentUrl = window.location.href;
        const currentHost = window.location.host;
        const currentPath = window.location.pathname;
        
        // Detect if we're in a preview deployment
        if (currentPath.includes('/branch-preview/')) {
            // Extract branch preview path
            const match = currentPath.match(/^(.*?)\/branch-preview\/([^\/]+)/);
            if (match) {
                this.baseUrl = `${window.location.protocol}//${currentHost}${match[1]}/branch-preview/${match[2]}`;
                this.deploymentType = 'preview';
            }
        } else {
            // Assume production deployment
            this.baseUrl = `${window.location.protocol}//${currentHost}`;
            this.deploymentType = 'production';
        }
        
        this.config = {
            baseUrl: this.baseUrl,
            deploymentType: this.deploymentType,
            urls: {
                schemas: `${this.baseUrl}/schema/`,
                libraries: `${this.baseUrl}/libraries/`,
                widgets: `${this.baseUrl}/widgets/`,
                notebooks: `${this.baseUrl}/notebooks/`
            }
        };
        
        console.log('📐 URL Service fallback initialized:', this.config);
    }
    
    /**
     * Get base URL for current deployment
     */
    getBaseUrl() {
        return this.baseUrl || window.location.origin;
    }
    
    /**
     * Get URL for a schema file
     */
    getSchemaUrl(schemaPath) {
        const baseUrl = this.getBaseUrl();
        const cleanPath = schemaPath.replace(/^\/+/, '');
        return `${baseUrl}/${cleanPath}`;
    }
    
    /**
     * Get URL for a library resource
     */
    getLibraryUrl(libraryName, filePath = '') {
        const baseUrl = this.getBaseUrl();
        const cleanFilePath = filePath.replace(/^\/+/, '');
        if (cleanFilePath) {
            return `${baseUrl}/libraries/${libraryName}/${cleanFilePath}`;
        } else {
            return `${baseUrl}/libraries/${libraryName}/`;
        }
    }
    
    /**
     * Get URL for a widget
     */
    getWidgetUrl(widgetId) {
        const baseUrl = this.getBaseUrl();
        return `${baseUrl}/widgets/${widgetId}/`;
    }
    
    /**
     * Get URL for a notebook
     */
    getNotebookUrl(notebookPath) {
        const baseUrl = this.getBaseUrl();
        const cleanPath = notebookPath.replace(/^\/+/, '');
        return `${baseUrl}/notebooks/${cleanPath}`;
    }
    
    /**
     * Get download URL for notebooks.jsonld
     */
    getNotebooksJsonLdUrl() {
        return this.getSchemaUrl('notebooks.jsonld');
    }
    
    /**
     * Get deployment information
     */
    getDeploymentInfo() {
        return {
            baseUrl: this.baseUrl,
            deploymentType: this.deploymentType,
            config: this.config
        };
    }
    
    /**
     * Generate absolute URL from relative path
     */
    resolveUrl(relativePath) {
        const baseUrl = this.getBaseUrl();
        const cleanPath = relativePath.replace(/^\/+/, '');
        return `${baseUrl}/${cleanPath}`;
    }
    
    /**
     * Check if URL needs to be updated for current deployment
     */
    updateUrl(url) {
        if (!url) return url;
        
        // If it's already a relative URL, resolve it
        if (url.startsWith('./') || url.startsWith('../') || url.startsWith('/')) {
            return this.resolveUrl(url);
        }
        
        // If it's an absolute URL pointing to the same repository, update it
        const baseUrl = this.getBaseUrl();
        const repoMatch = url.match(/https:\/\/([^\/]+)\/([^\/]+)\/([^\/]+)(\/.*)?/);
        if (repoMatch) {
            const [, host, owner, repo, path] = repoMatch;
            if (host.includes('github.io') && path) {
                return `${baseUrl}${path}`;
            }
        }
        
        return url;
    }
}

// Create global URL service instance
window.urlService = new URLService();

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = URLService;
}