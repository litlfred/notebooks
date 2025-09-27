# Branch Preview Deployment System

This repository implements a comprehensive branch preview deployment system for GitHub Pages that automatically handles URL generation and schema management across different deployment contexts.

## 🌟 Overview

The deployment system provides three types of deployments:

1. **🌿 Branch Previews** - Feature branches deployed to `{profile}.github.io/{repo}/branch-preview/{branch-name}`
2. **🔄 Main Preview** - Main branch deployed to `{profile}.github.io/{repo}/branch-preview/main`  
3. **🎯 Production** - Manual deployment to `{profile}.github.io/{repo}` (root URL)

## 🚀 Deployment Types

### Branch Preview Deployments

**Trigger**: Push to any feature branch or PR creation/updates
**URL Pattern**: `https://litlfred.github.io/notebooks/branch-preview/{branch-name}`
**Workflow**: `.github/workflows/branch-preview-deploy.yml`

- Automatically deploys every feature branch
- PR comments include preview links
- Schema URLs automatically adjusted for preview context
- Updates automatically on new commits

### Main Branch Preview

**Trigger**: Push to main branch or approved PR review
**URL Pattern**: `https://litlfred.github.io/notebooks/branch-preview/main`
**Workflow**: `.github/workflows/deploy.yml` (preview mode)

- Provides a staging environment for main branch
- Same behavior as branch previews but for main
- Safe testing before production deployment

### Production Deployment

**Trigger**: Manual workflow dispatch only
**URL Pattern**: `https://litlfred.github.io/notebooks`
**Workflow**: `.github/workflows/deploy.yml` (production mode)

- **Security**: Only available through GitHub UI workflow dispatch
- Deploys to root URL (production site)
- Requires manual trigger to prevent accidental production deployments

## 🛠️ Implementation Components

### 1. Python Deployment Manager (`scripts/deploy_manager.py`)

The core component that handles deployment context detection and URL management:

```bash
# Configure deployment context
python scripts/deploy_manager.py . configure

# View deployment information
python scripts/deploy_manager.py . info
```

**Features:**
- Detects deployment type from GitHub environment variables
- Updates Jekyll `_config.yml` with branch-aware URLs
- Dynamically updates all schema URLs in JSON/JSON-LD files
- Creates `deployment-info.json` for JavaScript access

**Environment Detection:**
- `GITHUB_REF` - Branch/PR reference
- `GITHUB_EVENT_NAME` - Trigger event type
- `INPUT_DEPLOY_TYPE` - Manual deployment type selection

### 2. JavaScript Deployment Utils (`docs/deployment-utils.js`)

Client-side utilities for deployment-aware applications:

```javascript
// Initialize deployment context
await window.deploymentUtils.initialize();

// Get schema URLs
const schemaUrl = window.deploymentUtils.getSchemaUrl('sticky-note', 'input.schema.json');

// Check deployment type
if (window.deploymentUtils.isProduction()) {
    console.log('Running in production mode');
}

// Get deployment info
const info = window.deploymentUtils.getDeploymentInfo();
console.log('Branch:', info.branch_name);
console.log('Schema Base:', info.schema_base_url);
```

### 3. Updated Workflows

**Branch Preview Workflow** (`.github/workflows/branch-preview-deploy.yml`):
- Handles feature branch and PR deployments
- Comments on PRs with preview links
- Concurrent deployments allowed per branch

**Main Deployment Workflow** (`.github/workflows/deploy.yml`):
- Handles main branch preview and production deployments
- Uses deployment type input to distinguish between preview/production
- Production deployment only via manual trigger

**PR Validation Workflow** (`.github/workflows/pr-preview.yml`):
- Validates PR readiness for deployment
- Tests deployment configuration
- Provides information about upcoming preview deployment

## 📋 Manual Deployment Instructions

### Deploying Branch Previews Manually

**NEW:** You can now manually deploy any branch for preview via GitHub UI:

1. Navigate to **Actions** tab in GitHub repository
2. Select **"🌿 Branch Preview Deployment"** workflow
3. Click **"Run workflow"**
4. **Branch Selection:**
   - Leave **Branch to deploy** empty to use current branch
   - Or enter specific branch name (e.g., `feature-xyz`)
5. Set **Preview deployment type**: `branch-preview` (default)
6. Click **"Run workflow"**

This creates a preview at: `https://litlfred.github.io/notebooks/branch-preview/{branch-name}`

### Deploying to Production

1. Navigate to **Actions** tab in GitHub repository
2. Select **"🚀 Deploy Mathematical Notebooks to GitHub Pages"** workflow
3. Click **"Run workflow"**
4. Select **Branch**: `main`
5. Set **Deploy type**: `production`
6. Click **"Run workflow"**

### Deploying Main Branch Preview

1. Navigate to **Actions** tab in GitHub repository
2. Select **"🚀 Deploy Mathematical Notebooks to GitHub Pages"** workflow  
3. Click **"Run workflow"**
4. Select **Branch**: `main`
5. Set **Deploy type**: `preview` (default)
6. Click **"Run workflow"**

## 🔧 Configuration Details

### Jekyll Configuration Updates

The deployment manager automatically updates `docs/_config.yml`:

```yaml
# Base configuration
url: "https://litlfred.github.io"
baseurl: "/notebooks/branch-preview/feature-branch"  # Dynamic based on context

# Auto-generated deployment context
deployment_type: "preview"
branch_name: "feature-branch"
schema_base_url: "https://litlfred.github.io/notebooks/branch-preview/feature-branch/schema"
```

### Schema URL Management

All schema files are automatically updated with deployment-aware URLs:

**Before** (hardcoded):
```json
{
  "$id": "https://litlfred.github.io/notebooks/schema/sticky-note/input.schema.json"
}
```

**After** (deployment-aware):
```json
{
  "$id": "https://litlfred.github.io/notebooks/branch-preview/feature-xyz/schema/sticky-note/input.schema.json"
}
```

### Deployment Info File

Each deployment creates `docs/deployment-info.json`:

```json
{
  "deployment_type": "preview",
  "branch_name": "feature-xyz",
  "base_url": "https://litlfred.github.io/notebooks/branch-preview/feature-xyz",
  "schema_base_url": "https://litlfred.github.io/notebooks/branch-preview/feature-xyz/schema",
  "is_production": false
}
```

## 🔍 Troubleshooting

### Common Issues

1. **Schema URLs not updating**: Check that `scripts/deploy_manager.py` runs successfully in workflow
2. **Preview not accessible**: Verify branch name doesn't contain invalid URL characters
3. **Production deployment blocked**: Ensure you're using manual workflow dispatch, not automatic triggers

### Debugging

Enable deployment info display by adding to your HTML:

```html
<!-- Add deployment info display -->
<div id="deployment-info-display"></div>

<script>
// Show deployment context
window.deploymentUtils.initialize().then(() => {
    window.deploymentUtils.displayDeploymentInfo('deployment-info-display');
});
</script>
```

### Logs and Monitoring

- **Workflow Logs**: Check GitHub Actions for deployment workflow execution
- **Browser Console**: Deployment utils log context information
- **Jekyll Build**: Review Jekyll build output for configuration issues

## 🛡️ Security Features

1. **Production Deployment Protection**: Only manual workflow dispatch can trigger production deployments
2. **No Credential Exposure**: All configuration through environment variables and GitHub context
3. **Branch Isolation**: Each branch gets its own preview URL space
4. **Automatic Cleanup**: Preview deployments are isolated and don't affect production

## 📚 Additional Resources

- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [GitHub Actions Workflow Syntax](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
- [Jekyll Configuration](https://jekyllrb.com/docs/configuration/)

## 🤝 Contributing

When adding new features that require schema URLs:

1. Use `window.deploymentUtils.getSchemaUrl()` in JavaScript
2. Reference schema files relatively when possible
3. Test with multiple deployment contexts (preview, production)
4. Update this documentation for significant changes