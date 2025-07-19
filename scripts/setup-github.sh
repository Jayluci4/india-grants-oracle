#!/bin/bash

# India Grants Oracle - GitHub Repository Setup Script
# This script helps you create and publish the project to GitHub

set -e

echo "🏗️ India Grants Oracle - GitHub Repository Setup"
echo "=================================================="

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first."
    exit 1
fi

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo "⚠️  GitHub CLI (gh) is not installed."
    echo "You can install it from: https://cli.github.com/"
    echo "Or create the repository manually on GitHub.com"
    echo ""
    read -p "Do you want to continue with manual setup? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Get repository name
REPO_NAME="india-grants-oracle"
echo "Repository name: $REPO_NAME"

# Get user input for GitHub username
read -p "Enter your GitHub username: " GITHUB_USERNAME

# Create .env.example if it doesn't exist
if [ ! -f ".env.example" ]; then
    echo "Creating .env.example file..."
    cat > .env.example << 'EOF'
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
EOF
fi

# Initialize git repository if not already done
if [ ! -d ".git" ]; then
    echo "Initializing git repository..."
    git init
fi

# Add all files
echo "Adding files to git..."
git add .

# Create initial commit
echo "Creating initial commit..."
git commit -m "Initial commit: India Grants Oracle - Multi-agent grant discovery system"

# Create repository on GitHub
if command -v gh &> /dev/null; then
    echo "Creating GitHub repository..."
    gh repo create "$REPO_NAME" \
        --public \
        --description "One source-of-truth for every non-dilutive rupee the Indian government offers startups" \
        --homepage "https://github.com/$GITHUB_USERNAME/$REPO_NAME" \
        --source . \
        --remote origin \
        --push
else
    echo "Please create the repository manually on GitHub.com:"
    echo "1. Go to https://github.com/new"
    echo "2. Repository name: $REPO_NAME"
    echo "3. Description: One source-of-truth for every non-dilutive rupee the Indian government offers startups"
    echo "4. Make it public"
    echo "5. Don't initialize with README (we already have one)"
    echo ""
    read -p "Press Enter after creating the repository..."
    
    # Add remote and push
    git remote add origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
    git branch -M main
    git push -u origin main
fi

# Update README with correct repository URL
echo "Updating README with correct repository URL..."
sed -i "s|YOUR_USERNAME|$GITHUB_USERNAME|g" README.md

# Commit the updated README
git add README.md
git commit -m "Update README with correct repository URL"
git push

echo ""
echo "✅ Repository setup complete!"
echo ""
echo "🌐 Your repository is now available at:"
echo "   https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo ""
echo "📋 Next steps:"
echo "1. Set up environment variables in GitHub Secrets"
echo "2. Configure CI/CD pipeline"
echo "3. Add collaborators if needed"
echo "4. Set up deployment pipeline"
echo ""
echo "🔧 To set up environment variables:"
echo "   Go to Settings > Secrets and variables > Actions"
echo "   Add OPENAI_API_KEY and other required secrets"
echo ""
echo "🚀 Happy coding!" 