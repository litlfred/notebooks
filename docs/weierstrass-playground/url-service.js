/**
 * URL Service for Environment-Aware URL Generation
 * Handles different deployment contexts: production, preview, and local development
 */

class URLService {
    constructor() {
        this.baseUrl = this.detectBaseUrl();
        this.deploymentContext = this.detectDeploymentContext();
        this.schemaBaseUrl = this.getSchemaBaseUrl();
        
        console.log('URLService initialized:', {
            baseUrl: this.baseUrl,
            context: this.deploymentContext,
            schemaBase: this.schemaBaseUrl
        });
    }

    /**
     * Detect the base URL based on current location
     */
    detectBaseUrl() {
        if (typeof window === 'undefined') {
            // Server-side or testing environment
            return process.env.GITHUB_PAGES_BASE_URL || 'https://litlfred.github.io/notebooks';
        }

        const currentUrl = window.location.href;
        const origin = window.location.origin;
        const pathname = window.location.pathname;

        // Local development
        if (origin.includes('localhost') || origin.includes('127.0.0.1')) {
            return origin;
        }

        // GitHub Pages - extract base path
        if (origin.includes('github.io')) {
            // Check if we're in a preview branch deployment
            const previewMatch = pathname.match(/^\/([^\/]+)\/branch-preview\/([^\/]+)/);
            if (previewMatch) {
                const [, repo, branch] = previewMatch;
                return `${origin}/${repo}/branch-preview/${branch}`;
            }

            // Check if we're in the main repository
            const repoMatch = pathname.match(/^\/([^\/]+)/);
            if (repoMatch) {
                const [, repo] = repoMatch;
                return `${origin}/${repo}`;
            }
        }

        // Fallback
        return origin;
    }

    /**
     * Detect deployment context (production, preview, or local)
     */
    detectDeploymentContext() {
        if (typeof window === 'undefined') {
            return process.env.DEPLOYMENT_CONTEXT || 'production';
        }

        const pathname = window.location.pathname;
        const hostname = window.location.hostname;

        if (hostname.includes('localhost') || hostname.includes('127.0.0.1')) {
            return 'local';
        }

        if (pathname.includes('/branch-preview/')) {
            return 'preview';
        }

        return 'production';
    }

    /**
     * Get schema base URL - always use production for schema consistency
     */
    getSchemaBaseUrl() {
        // Environment variable override for testing
        if (typeof process !== 'undefined' && process.env.SCHEMA_BASE_URL) {
            return process.env.SCHEMA_BASE_URL;
        }

        // Always use production schemas for consistency
        return 'https://litlfred.github.io/notebooks';
    }

    /**
     * Generate schema URL for a widget type
     */
    getSchemaUrl(widgetType, schemaType = 'widget.schema.json') {
        return `${this.schemaBaseUrl}/schema/${widgetType}/${schemaType}`;
    }

    /**
     * Generate context URL for JSON-LD
     */
    getContextUrl(contextPath) {
        if (contextPath.startsWith('http')) {
            return contextPath;
        }
        return `${this.schemaBaseUrl}/${contextPath}`;
    }

    /**
     * Generate absolute URL for resources within the current deployment
     */
    getResourceUrl(relativePath) {
        if (relativePath.startsWith('http')) {
            return relativePath;
        }
        
        // Remove leading slash if present
        const cleanPath = relativePath.replace(/^\//, '');
        return `${this.baseUrl}/${cleanPath}`;
    }

    /**
     * Generate URL for downloading notebooks
     */
    getNotebookDownloadUrl(notebookId) {
        return `${this.baseUrl}/notebooks/${notebookId}.jsonld`;
    }

    /**
     * Generate URL for widget schemas registry
     */
    getWidgetSchemasUrl() {
        return `${this.baseUrl}/weierstrass-playground/widget-schemas.json`;
    }

    /**
     * Generate URL for the board application
     */
    getBoardUrl() {
        return `${this.baseUrl}/weierstrass-playground/board.html`;
    }

    /**
     * Get deployment info for debugging and status display
     */
    getDeploymentInfo() {
        return {
            baseUrl: this.baseUrl,
            context: this.deploymentContext,
            schemaBaseUrl: this.schemaBaseUrl,
            isPreview: this.deploymentContext === 'preview',
            isProduction: this.deploymentContext === 'production',
            isLocal: this.deploymentContext === 'local',
            branchName: this.getBranchName()
        };
    }

    /**
     * Extract branch name from preview URL
     */
    getBranchName() {
        if (this.deploymentContext !== 'preview') {
            return null;
        }

        if (typeof window === 'undefined') {
            return process.env.GITHUB_REF_NAME || null;
        }

        const pathname = window.location.pathname;
        const match = pathname.match(/\/branch-preview\/([^\/]+)/);
        return match ? match[1] : null;
    }

    /**
     * Generate JSON-LD context with environment-aware URLs
     */
    generateJsonLdContext() {
        return [
            "https://www.w3.org/ns/prov-o.jsonld",
            this.getContextUrl("schema/ontology/context.jsonld")
        ];
    }

    /**
     * Update existing URLs in data to be environment-aware
     */
    updateUrlsInData(data) {
        if (typeof data === 'string') {
            // Replace hardcoded URLs with environment-aware ones
            return data
                .replace(/https:\/\/litlfred\.github\.io\/notebooks/g, this.baseUrl)
                .replace(/\"\/schema\//g, `"${this.schemaBaseUrl}/schema/`)
                .replace(/\"\/weierstrass-playground\//g, `"${this.baseUrl}/weierstrass-playground/`);
        }

        if (Array.isArray(data)) {
            return data.map(item => this.updateUrlsInData(item));
        }

        if (data && typeof data === 'object') {
            const updated = {};
            for (const [key, value] of Object.entries(data)) {
                updated[key] = this.updateUrlsInData(value);
            }
            return updated;
        }

        return data;
    }
}

// Global instance
window.urlService = new URLService();

// Export for Node.js environments
if (typeof module !== 'undefined' && module.exports) {
    module.exports = URLService;
}