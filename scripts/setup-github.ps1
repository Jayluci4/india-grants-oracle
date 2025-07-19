# India Grants Oracle - GitHub Repository Setup Script (PowerShell)
# This script helps you create and publish the project to GitHub

param(
    [string]$GitHubUsername = "",
    [string]$RepoName = "india-grants-oracle"
)

Write-Host "🏗️ India Grants Oracle - GitHub Repository Setup" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green

# Check if git is installed
try {
    git --version | Out-Null
    Write-Host "✅ Git is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Git is not installed. Please install Git first." -ForegroundColor Red
    Write-Host "Download from: https://git-scm.com/downloads" -ForegroundColor Yellow
    exit 1
}

# Check if GitHub CLI is installed
try {
    gh --version | Out-Null
    $HasGitHubCLI = $true
    Write-Host "✅ GitHub CLI is installed" -ForegroundColor Green
} catch {
    $HasGitHubCLI = $false
    Write-Host "⚠️  GitHub CLI (gh) is not installed." -ForegroundColor Yellow
    Write-Host "You can install it from: https://cli.github.com/" -ForegroundColor Yellow
    Write-Host "Or create the repository manually on GitHub.com" -ForegroundColor Yellow
}

# Get GitHub username if not provided
if (-not $GitHubUsername) {
    $GitHubUsername = Read-Host "Enter your GitHub username"
}

Write-Host "Repository name: $RepoName" -ForegroundColor Cyan
Write-Host "GitHub username: $GitHubUsername" -ForegroundColor Cyan

# Create .env.example if it doesn't exist
if (-not (Test-Path ".env.example")) {
    Write-Host "Creating .env.example file..." -ForegroundColor Yellow
    @"
# OpenAI API Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here

# Database Configuration
DATABASE_URL=postgresql://grants:grants@localhost:5432/grantsdb
# For SQLite (development)
# DATABASE_URL=sqlite:///grants.db

# Redis Configuration (for caching)
REDIS_URL=redis://localhost:6379

# Slack Notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
SLACK_CHANNEL=#grants-feed

# WhatsApp Notifications (Twilio)
TWILIO_SID=ACyour-twilio-sid-here
TWILIO_TOKEN=your-twilio-token-here
TWILIO_PHONE_NUMBER=+1234567890

# Application Configuration
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Scrapy Settings
SCRAPY_DELAY=2
SCRAPY_CONCURRENT_REQUESTS=1
SCRAPY_USER_AGENT=Mozilla/5.0 (compatible; IndiaGrantsOracle/1.0)

# AI Model Configuration
MAGENTIC_MODEL=gpt-4
MAGENTIC_TEMPERATURE=0.1
MAGENTIC_MAX_TOKENS=4000

# Notification Settings
ENABLE_SLACK_NOTIFICATIONS=true
ENABLE_WHATSAPP_NOTIFICATIONS=false
ENABLE_EMAIL_NOTIFICATIONS=false

# Discovery Settings
DISCOVERY_INTERVAL_HOURS=24
DEADLINE_CHECK_INTERVAL_HOURS=168  # Weekly
MAX_GRANTS_PER_DISCOVERY=100
"@ | Out-File -FilePath ".env.example" -Encoding UTF8
}

# Initialize git repository if not already done
if (-not (Test-Path ".git")) {
    Write-Host "Initializing git repository..." -ForegroundColor Yellow
    git init
}

# Add all files
Write-Host "Adding files to git..." -ForegroundColor Yellow
git add .

# Create initial commit
Write-Host "Creating initial commit..." -ForegroundColor Yellow
git commit -m "Initial commit: India Grants Oracle - Multi-agent grant discovery system"

# Create repository on GitHub
if ($HasGitHubCLI) {
    Write-Host "Creating GitHub repository..." -ForegroundColor Yellow
    gh repo create $RepoName `
        --public `
        --description "One source-of-truth for every non-dilutive rupee the Indian government offers startups" `
        --homepage "https://github.com/$GitHubUsername/$RepoName" `
        --source . `
        --remote origin `
        --push
} else {
    Write-Host "Please create the repository manually on GitHub.com:" -ForegroundColor Yellow
    Write-Host "1. Go to https://github.com/new" -ForegroundColor White
    Write-Host "2. Repository name: $RepoName" -ForegroundColor White
    Write-Host "3. Description: One source-of-truth for every non-dilutive rupee the Indian government offers startups" -ForegroundColor White
    Write-Host "4. Make it public" -ForegroundColor White
    Write-Host "5. Don't initialize with README (we already have one)" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter after creating the repository"
    
    # Add remote and push
    git remote add origin "https://github.com/$GitHubUsername/$RepoName.git"
    git branch -M main
    git push -u origin main
}

# Update README with correct repository URL
Write-Host "Updating README with correct repository URL..." -ForegroundColor Yellow
$readmeContent = Get-Content "README.md" -Raw
$readmeContent = $readmeContent -replace "YOUR_USERNAME", $GitHubUsername
$readmeContent | Out-File -FilePath "README.md" -Encoding UTF8

# Commit the updated README
git add README.md
git commit -m "Update README with correct repository URL"
git push

Write-Host ""
Write-Host "✅ Repository setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Your repository is now available at:" -ForegroundColor Cyan
Write-Host "   https://github.com/$GitHubUsername/$RepoName" -ForegroundColor White
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Yellow
Write-Host "1. Set up environment variables in GitHub Secrets" -ForegroundColor White
Write-Host "2. Configure CI/CD pipeline" -ForegroundColor White
Write-Host "3. Add collaborators if needed" -ForegroundColor White
Write-Host "4. Set up deployment pipeline" -ForegroundColor White
Write-Host ""
Write-Host "🔧 To set up environment variables:" -ForegroundColor Yellow
Write-Host "   Go to Settings > Secrets and variables > Actions" -ForegroundColor White
Write-Host "   Add OPENAI_API_KEY and other required secrets" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Happy coding!" -ForegroundColor Green 