/**
 * GitHub Pages Widget Launcher
 * Convenience class for handling widget instantiation under GitHub Pages context
 * Replaces iframe-based loading with direct navigation
 */

class GitHubPagesLauncher {
    constructor(config = {}) {
        this.config = {
            threadPoolWorkers: 4,
            enableLazyLoading: true,
            preloadScientific: true,
            playgroundPath: 'docs/weierstrass-playground/board.html',
            showLoadingScreen: true,
            loadingDelay: 1000,
            ...config
        };
        
        this.loadingStates = [
            'Initializing thread pool engine...',
            'Loading Python libraries...',
            'Setting up execution context...',
            'Preparing mathematical workspace...'
        ];
        
        this.currentStateIndex = 0;
        this.loadingInterval = null;
    }

    /**
     * Initialize and launch the widget playground
     */
    async launch() {
        try {
            if (this.config.showLoadingScreen) {
                this.showLoadingScreen();
                await this.simulateInitialization();
            }
            
            // Navigate directly to playground instead of using iframe
            this.navigateToPlayground();
            
        } catch (error) {
            this.showError('Failed to launch playground', error);
        }
    }

    /**
     * Show loading screen with progress updates
     */
    showLoadingScreen() {
        const loadingContainer = document.getElementById('loading-container');
        const loadingDetails = document.getElementById('loading-details');
        
        if (loadingContainer) {
            loadingContainer.style.display = 'flex';
        }
        
        // Animate through loading states
        this.loadingInterval = setInterval(() => {
            if (this.currentStateIndex < this.loadingStates.length && loadingDetails) {
                loadingDetails.textContent = this.loadingStates[this.currentStateIndex];
                this.currentStateIndex++;
            }
        }, 600);
    }

    /**
     * Simulate initialization process
     */
    async simulateInitialization() {
        // Simulate thread pool and context setup
        await this.delay(this.config.loadingDelay);
        
        // In GitHub Pages context, we don't actually initialize thread pools,
        // but we simulate the process for user experience
        console.log('GitHub Pages Widget Launcher: Simulating thread pool initialization');
        
        if (this.config.enableLazyLoading) {
            console.log('GitHub Pages Widget Launcher: Lazy loading enabled');
        }
    }

    /**
     * Navigate directly to playground without iframe
     */
    navigateToPlayground() {
        if (this.loadingInterval) {
            clearInterval(this.loadingInterval);
        }
        
        // Navigate directly to the playground page
        window.location.href = this.config.playgroundPath;
        
        // If we're staying on the same page (for testing), initialize threading bridge
        if (this.config.enableThreadingBridge && window.boardApp) {
            this.initializeThreadingBridge();
        }
    }

    /**
     * Initialize threading bridge if board app is available
     */
    async initializeThreadingBridge() {
        try {
            // Wait for board app to be fully loaded
            if (typeof BoardThreadingBridge === 'undefined') {
                console.warn('BoardThreadingBridge not available, skipping integration');
                return;
            }

            // Create threading bridge
            const bridge = new BoardThreadingBridge(window.boardApp, null);
            await bridge.initialize();

            // Store bridge globally for access
            window.threadingBridge = bridge;

            console.log('✅ Threading bridge initialized successfully');

        } catch (error) {
            console.error('❌ Failed to initialize threading bridge:', error);
        }
    }

    /**
     * Show error screen
     */
    showError(message, error) {
        if (this.loadingInterval) {
            clearInterval(this.loadingInterval);
        }
        
        const loadingContainer = document.getElementById('loading-container');
        const errorContainer = document.getElementById('error-container');
        const errorMessage = document.getElementById('error-message');
        const errorDetails = document.getElementById('error-details');
        
        if (loadingContainer) {
            loadingContainer.style.display = 'none';
        }
        
        if (errorContainer) {
            errorContainer.style.display = 'flex';
        }
        
        if (errorMessage) {
            errorMessage.textContent = message;
        }
        
        if (errorDetails && error) {
            errorDetails.textContent = error.toString();
        }
        
        console.error('GitHub Pages Widget Launcher Error:', message, error);
    }

    /**
     * Utility delay function
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Static factory method for GitHub Pages context
     */
    static createForGitHubPages(customConfig = {}) {
        const defaultGitHubPagesConfig = {
            threadPoolWorkers: 4,
            enableLazyLoading: true,
            preloadScientific: true,
            playgroundPath: 'docs/weierstrass-playground/board.html',
            showLoadingScreen: true,
            loadingDelay: 800,
            enableThreadingBridge: true
        };
        
        return new GitHubPagesLauncher({
            ...defaultGitHubPagesConfig,
            ...customConfig
        });
    }
}

// Export for module usage or make globally available
if (typeof module !== 'undefined' && module.exports) {
    module.exports = GitHubPagesLauncher;
} else {
    window.GitHubPagesLauncher = GitHubPagesLauncher;
}