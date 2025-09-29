/**
 * GitHub Personal Access Token Authentication Service
 * Handles authentication, user permissions, and GitHub API operations
 */

class GitHubAuthService {
    constructor() {
        this.token = localStorage.getItem('github_pat');
        this.username = localStorage.getItem('github_username');
        this.userPermissions = null;
        this.isAuthenticated = false;
        this.repoOwner = 'litlfred';
        this.repoName = 'notebooks';
        
        this.initializeAuth();
    }

    /**
     * Initialize authentication state on page load
     */
    initializeAuth() {
        if (this.token && this.username) {
            this.validateToken().then(valid => {
                if (valid) {
                    this.isAuthenticated = true;
                    this.checkUserPermissions();
                    this.updateUI();
                    this.integrateWithNotebookLoader();
                } else {
                    this.clearAuth();
                }
            });
        }
        this.setupAuthUI();
    }

    /**
     * Setup authentication UI elements
     */
    setupAuthUI() {
        // Add login modal to the page
        this.createLoginModal();
        // Add authentication controls to header
        this.addAuthControls();
    }

    /**
     * Create login modal with PAT instructions
     */
    createLoginModal() {
        const modal = document.createElement('div');
        modal.id = 'github-auth-modal';
        modal.className = 'auth-modal';
        modal.innerHTML = `
            <div class="auth-modal-content">
                <div class="auth-modal-header">
                    <h3><i class="fab fa-github"></i> GitHub Authentication</h3>
                    <button class="close-modal" onclick="githubAuth.closeLoginModal()">&times;</button>
                </div>
                
                <div class="auth-modal-body">
                    <p>Authenticate with GitHub to save and edit notebooks in the repository.</p>
                    
                    <form id="github-auth-form" onsubmit="githubAuth.handleLogin(event)">
                        <div class="form-group">
                            <label for="github-username">GitHub Username:</label>
                            <input type="text" id="github-username" name="username" required
                                   placeholder="Your GitHub username" autocomplete="username">
                        </div>
                        
                        <div class="form-group">
                            <label for="github-pat">Personal Access Token:</label>
                            <input type="password" id="github-pat" name="token" required
                                   placeholder="ghp_..." autocomplete="current-password">
                        </div>
                        
                        <div class="auth-instructions">
                            <h4>How to Generate a Personal Access Token (PAT):</h4>
                            <ol>
                                <li>Go to <a href="https://github.com/settings/tokens" target="_blank">GitHub Settings → Developer settings → Personal access tokens</a></li>
                                <li>Click "Generate new token (classic)"</li>
                                <li>Give it a descriptive name like "Mathematical Notebooks"</li>
                                <li>Select these scopes:
                                    <ul>
                                        <li><strong>repo</strong> - Full control of private repositories</li>
                                        <li><strong>write:repo-hook</strong> - Write repository hooks</li>
                                    </ul>
                                </li>
                                <li>Click "Generate token" and copy the token</li>
                                <li>Paste the token in the field above</li>
                            </ol>
                            <p><strong>Note:</strong> Your credentials are stored locally in your browser and are never sent to third parties.</p>
                        </div>
                        
                        <div class="auth-buttons">
                            <button type="submit" class="auth-btn primary">Login</button>
                            <button type="button" class="auth-btn secondary" onclick="githubAuth.closeLoginModal()">Cancel</button>
                        </div>
                    </form>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    }

    /**
     * Add authentication controls to the board header
     */
    addAuthControls() {
        const boardHeader = document.querySelector('.board-header .board-tools');
        if (!boardHeader) return;

        const authControls = document.createElement('div');
        authControls.className = 'auth-controls';
        authControls.innerHTML = `
            <div id="auth-status" class="auth-status">
                <button class="tool-btn" id="auth-login-btn" onclick="githubAuth.showLoginModal()">
                    <i class="fab fa-github"></i> Login
                </button>
            </div>
        `;
        
        boardHeader.appendChild(authControls);
    }

    /**
     * Show login modal
     */
    showLoginModal() {
        const modal = document.getElementById('github-auth-modal');
        if (modal) {
            modal.style.display = 'flex';
            // Focus on username field
            setTimeout(() => {
                document.getElementById('github-username').focus();
            }, 100);
        }
    }

    /**
     * Close login modal
     */
    closeLoginModal() {
        const modal = document.getElementById('github-auth-modal');
        if (modal) {
            modal.style.display = 'none';
        }
    }

    /**
     * Handle login form submission
     */
    async handleLogin(event) {
        event.preventDefault();
        
        const username = document.getElementById('github-username').value.trim();
        const token = document.getElementById('github-pat').value.trim();
        
        if (!username || !token) {
            this.showError('Please provide both username and token');
            return;
        }

        // Show loading state
        const submitBtn = event.target.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Authenticating...';
        submitBtn.disabled = true;

        try {
            // Validate credentials
            const isValid = await this.validateCredentials(username, token);
            
            if (isValid) {
                // Store credentials
                this.username = username;
                this.token = token;
                localStorage.setItem('github_username', username);
                localStorage.setItem('github_pat', token);
                
                this.isAuthenticated = true;
                await this.checkUserPermissions();
                this.updateUI();
                this.integrateWithNotebookLoader();
                this.closeLoginModal();
                this.showSuccess('Successfully authenticated with GitHub!');
            } else {
                this.showError('Invalid credentials. Please check your username and token.');
            }
        } catch (error) {
            console.error('Authentication error:', error);
            this.showError('Authentication failed. Please try again.');
        } finally {
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        }
    }

    /**
     * Validate GitHub credentials
     */
    async validateCredentials(username, token) {
        try {
            const response = await fetch('https://api.github.com/user', {
                headers: {
                    'Authorization': `token ${token}`,
                    'Accept': 'application/vnd.github.v3+json',
                    'X-GitHub-Api-Version': '2022-11-28'
                }
            });

            if (response.ok) {
                const userData = await response.json();
                return userData.login.toLowerCase() === username.toLowerCase();
            }
            return false;
        } catch (error) {
            console.error('Validation error:', error);
            return false;
        }
    }

    /**
     * Validate stored token
     */
    async validateToken() {
        if (!this.token) return false;
        return this.validateCredentials(this.username, this.token);
    }

    /**
     * Check user permissions for the repository
     */
    async checkUserPermissions() {
        if (!this.isAuthenticated) return;

        try {
            // Check if user is a collaborator
            const response = await fetch(
                `https://api.github.com/repos/${this.repoOwner}/${this.repoName}/collaborators/${this.username}`,
                {
                    headers: {
                        'Authorization': `token ${this.token}`,
                        'Accept': 'application/vnd.github.v3+json'
                    }
                }
            );

            this.userPermissions = {
                isCollaborator: response.status === 204,
                canWrite: response.status === 204,
                canDelete: response.status === 204
            };

            // Also check repository access
            const repoResponse = await fetch(
                `https://api.github.com/repos/${this.repoOwner}/${this.repoName}`,
                {
                    headers: {
                        'Authorization': `token ${this.token}`,
                        'Accept': 'application/vnd.github.v3+json'
                    }
                }
            );

            if (repoResponse.ok) {
                const repoData = await repoResponse.json();
                this.userPermissions.canWrite = this.userPermissions.canWrite || 
                    (repoData.permissions && (repoData.permissions.push || repoData.permissions.admin));
            }

        } catch (error) {
            console.error('Error checking permissions:', error);
            this.userPermissions = {
                isCollaborator: false,
                canWrite: false,
                canDelete: false
            };
        }
    }

    /**
     * Update UI based on authentication state
     */
    updateUI() {
        const authStatus = document.getElementById('auth-status');
        if (!authStatus) return;

        if (this.isAuthenticated) {
            const canWrite = this.userPermissions?.canWrite || false;
            
            authStatus.innerHTML = `
                <div class="user-info">
                    <span class="username"><i class="fab fa-github"></i> ${this.username}</span>
                    <div class="user-actions">
                        ${canWrite ? `
                            <button class="tool-btn success" onclick="githubAuth.saveToGitHub()" title="Save to GitHub">
                                <i class="fas fa-save"></i> Save to GitHub
                            </button>
                            <button class="tool-btn" onclick="githubAuth.createNewNotebook()" title="Create New Notebook">
                                <i class="fas fa-plus"></i> New Notebook
                            </button>
                        ` : ''}
                        <button class="tool-btn secondary" onclick="githubAuth.logout()" title="Logout">
                            <i class="fas fa-sign-out-alt"></i>
                        </button>
                    </div>
                </div>
            `;

            // Add repository permissions info
            if (this.userPermissions) {
                const permissionText = this.userPermissions.canWrite ? 
                    'Write access' : 'Read-only access';
                authStatus.setAttribute('title', `${permissionText} to ${this.repoOwner}/${this.repoName}`);
            }
        } else {
            authStatus.innerHTML = `
                <button class="tool-btn" onclick="githubAuth.showLoginModal()">
                    <i class="fab fa-github"></i> Login
                </button>
            `;
        }
    }

    /**
     * Save current notebook to GitHub (updated for PR #15 integration)
     */
    async saveToGitHub() {
        if (!this.canWrite()) {
            this.showError('You do not have write permissions for this repository.');
            return;
        }

        try {
            // Get current notebook state using the enhanced format
            const notebookData = this.getCurrentNotebookData();
            const filename = this.generateNotebookFilename();
            
            // Generate commit message
            const commitMessage = this.generateCommitMessage(filename, 'update');
            
            await this.saveFileToGitHub(`notebooks/${filename}`, notebookData, commitMessage);
            this.showSuccess('Notebook saved to GitHub successfully!');
            
            // Integrate with notebook loader if available
            if (window.notebookLoader) {
                window.notebookLoader.loadAvailableNotebooks();
            }
            
        } catch (error) {
            console.error('Save error:', error);
            this.showError('Failed to save notebook to GitHub.');
        }
    }

    /**
     * Create a new empty notebook
     */
    async createNewNotebook() {
        if (!this.canWrite()) {
            this.showError('You do not have write permissions for this repository.');
            return;
        }

        try {
            const emptyNotebook = this.createEmptyNotebook();
            const filename = this.generateNotebookFilename('new-notebook');
            const commitMessage = this.generateCommitMessage(filename, 'create');
            
            await this.saveFileToGitHub(`notebooks/${filename}`, emptyNotebook, commitMessage);
            this.showSuccess('New notebook created successfully!');
            
            // Optionally load the new notebook
            // this.loadNotebook(filename);
            
        } catch (error) {
            console.error('Create error:', error);
            this.showError('Failed to create new notebook.');
        }
    }

    /**
     * Save file to GitHub repository
     */
    async saveFileToGitHub(path, content, message) {
        const url = `https://api.github.com/repos/${this.repoOwner}/${this.repoName}/contents/${path}`;
        
        // First, try to get the existing file to get its SHA
        let sha = null;
        try {
            const existingResponse = await fetch(url, {
                headers: {
                    'Authorization': `token ${this.token}`,
                    'Accept': 'application/vnd.github.v3+json'
                }
            });
            
            if (existingResponse.ok) {
                const existingFile = await existingResponse.json();
                sha = existingFile.sha;
            }
        } catch (error) {
            // File doesn't exist, which is fine for new files
        }

        // Create or update the file
        const requestBody = {
            message: message,
            content: btoa(unescape(encodeURIComponent(content))), // Base64 encode
            branch: 'main'
        };
        
        if (sha) {
            requestBody.sha = sha; // Required for updates
        }

        const response = await fetch(url, {
            method: 'PUT',
            headers: {
                'Authorization': `token ${this.token}`,
                'Accept': 'application/vnd.github.v3+json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || 'Failed to save file');
        }

        return response.json();
    }

    /**
     * Get current notebook data as JSON-LD (compatible with PR #15 format)
     */
    getCurrentNotebookData() {
        const board = window.mathematicalBoard;
        if (!board) {
            throw new Error('Board not initialized');
        }

        const title = document.getElementById('board-title')?.textContent || "Mathematical Notebook";
        const notebookId = this.generateNotebookId(title);
        
        const notebookData = {
            "@context": [
                "https://www.w3.org/ns/prov-o.jsonld",
                "https://litlfred.github.io/notebooks/schema/ontology/context.jsonld"
            ],
            "@id": notebookId,
            "@type": ["prov:Collection", "notebook:Notebook"],
            "notebook:title": title,
            "notebook:description": `Mathematical notebook created by ${this.username}`,
            "notebook:created": new Date().toISOString(),
            "notebook:version": "1.0.0",
            "notebook:creator": this.username,
            "notebook:layout": {
                "canvas_size": {"width": 1200, "height": 800},
                "zoom_level": 1.0,
                "center_point": {"x": 600, "y": 400}
            },
            "prov:hadMember": []
        };

        // Add current widgets using PR #15 format
        if (board.widgets && board.widgets.size > 0) {
            let widgetIndex = 1;
            board.widgets.forEach((widget, id) => {
                const widgetId = `urn:widget:${widget.type}-${widgetIndex}`;
                notebookData["prov:hadMember"].push({
                    "@id": widgetId,
                    "@type": ["prov:Entity", `${widget.type}:widget`],
                    "dct:conformsTo": `https://litlfred.github.io/notebooks/schema/${widget.type}/widget.schema.json`,
                    "notebook:position": widget.position || {"x": 100 + (widgetIndex * 50), "y": 100 + (widgetIndex * 50)},
                    "notebook:size": widget.size || {"width": 300, "height": 250},
                    "notebook:config": widget.configuration || {},
                    "prov:generatedAtTime": new Date().toISOString()
                });
                widgetIndex++;
            });
        }

        return JSON.stringify(notebookData, null, 2);
    }

    /**
     * Generate a URN-compliant notebook ID
     */
    generateNotebookId(title) {
        const safeTitle = title.toLowerCase()
            .replace(/[^a-z0-9\s-]/g, '')
            .replace(/\s+/g, '-')
            .replace(/-+/g, '-')
            .trim();
        return `urn:notebook:${safeTitle}`;
    }

    /**
     * Create empty notebook structure (compatible with PR #15 format)
     */
    createEmptyNotebook() {
        const title = "New Mathematical Notebook";
        const notebookId = this.generateNotebookId(title);
        
        const emptyNotebook = {
            "@context": [
                "https://www.w3.org/ns/prov-o.jsonld",
                "https://litlfred.github.io/notebooks/schema/ontology/context.jsonld"
            ],
            "@id": notebookId,
            "@type": ["prov:Collection", "notebook:Notebook"],
            "notebook:title": title,
            "notebook:description": `Empty mathematical notebook template created by ${this.username}`,
            "notebook:created": new Date().toISOString(),
            "notebook:version": "1.0.0",
            "notebook:creator": this.username,
            "notebook:layout": {
                "canvas_size": {"width": 1200, "height": 800},
                "zoom_level": 1.0,
                "center_point": {"x": 600, "y": 400}
            },
            "prov:hadMember": [
                {
                    "@id": "urn:widget:sticky-note-welcome",
                    "@type": ["prov:Entity", "sticky:widget"],
                    "dct:conformsTo": "https://litlfred.github.io/notebooks/schema/sticky-note/widget.schema.json",
                    "notebook:position": {"x": 100, "y": 100},
                    "notebook:size": {"width": 300, "height": 200},
                    "notebook:config": {
                        "content": "# Welcome!\n\nThis is your new mathematical notebook. Start by:\n\n1. Adding widgets from the library\n2. Configuring mathematical parameters\n3. Creating visualizations\n4. Saving your work to GitHub",
                        "theme": "desert",
                        "show_note": true,
                        "editable": true
                    },
                    "prov:generatedAtTime": new Date().toISOString()
                }
            ]
        };

        return JSON.stringify(emptyNotebook, null, 2);
    }

    /**
     * Generate notebook filename
     */
    generateNotebookFilename(baseName = null) {
        const title = baseName || document.getElementById('board-title')?.textContent || 'notebook';
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
        const safeTitle = title.toLowerCase()
            .replace(/[^a-z0-9\s-]/g, '')
            .replace(/\s+/g, '-')
            .replace(/-+/g, '-')
            .trim();
        
        return `${safeTitle}-${timestamp}.jsonld`;
    }

    /**
     * Generate commit message
     */
    generateCommitMessage(filename, action) {
        const messages = {
            create: `Create notebook: ${filename}`,
            update: `Update notebook: ${filename}`,
            delete: `Remove notebook: ${filename}`
        };
        
        return messages[action] || `Modify notebook: ${filename}`;
    }

    /**
     * Check if user can write to repository
     */
    canWrite() {
        return this.isAuthenticated && this.userPermissions?.canWrite;
    }

    /**
     * Logout user
     */
    logout() {
        this.clearAuth();
        this.showSuccess('Logged out successfully.');
    }

    /**
     * Clear authentication data
     */
    clearAuth() {
        this.token = null;
        this.username = null;
        this.userPermissions = null;
        this.isAuthenticated = false;
        
        localStorage.removeItem('github_pat');
        localStorage.removeItem('github_username');
        
        this.updateUI();
    }

    /**
     * Show success message
     */
    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    /**
     * Show error message
     */
    showError(message) {
        this.showNotification(message, 'error');
    }

    /**
     * Show notification
     */
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-message">${message}</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">&times;</button>
            </div>
        `;

        // Add to page
        document.body.appendChild(notification);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

    /**
     * Integrate with NotebookLoader for GitHub operations
     */
    integrateWithNotebookLoader() {
        if (window.notebookLoader) {
            // Extend NotebookLoader with GitHub functionality
            window.notebookLoader.saveToGitHub = this.saveToGitHub.bind(this);
            window.notebookLoader.loadFromGitHub = this.loadFromGitHub.bind(this);
            window.notebookLoader.createNewNotebook = this.createNewNotebook.bind(this);
        }
    }

    /**
     * Load notebook from GitHub repository
     */
    async loadFromGitHub(filename) {
        if (!this.canWrite()) {
            this.showError('You need write permissions to load from GitHub.');
            return;
        }

        try {
            const url = `https://api.github.com/repos/${this.repoOwner}/${this.repoName}/contents/notebooks/${filename}`;
            const response = await fetch(url, {
                headers: {
                    'Authorization': `token ${this.token}`,
                    'Accept': 'application/vnd.github.v3+json'
                }
            });

            if (!response.ok) {
                throw new Error(`Failed to load from GitHub: ${response.statusText}`);
            }

            const fileData = await response.json();
            const content = atob(fileData.content);
            const notebook = JSON.parse(content);
            
            // Load using the existing notebook loader
            if (window.notebookLoader) {
                await window.notebookLoader.loadNotebookData(notebook);
                this.showSuccess(`Loaded notebook from GitHub: ${filename}`);
            }
        } catch (error) {
            console.error('GitHub load error:', error);
            this.showError(`Failed to load from GitHub: ${error.message}`);
        }
    }
}

// Initialize GitHub authentication service
window.githubAuth = new GitHubAuthService();