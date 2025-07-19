# 🚀 GitHub Repository Setup Guide

This guide will help you create and publish the India Grants Oracle project to GitHub.

## 📋 Prerequisites

1. **Git** installed on your system
   - Download from: https://git-scm.com/downloads
   - Verify installation: `git --version`

2. **GitHub Account**
   - Create at: https://github.com
   - Note down your username

3. **GitHub CLI (Optional but Recommended)**
   - Download from: https://cli.github.com/
   - Install and authenticate: `gh auth login`

## 🎯 Quick Setup (Automated)

### Option 1: Using PowerShell Script (Windows)

```powershell
# Navigate to your project directory
cd "C:\Users\Jayan\Downloads\enhanced-india-grants-oracle-v2\india-grants-oracle"

# Run the setup script
.\scripts\setup-github.ps1
```

### Option 2: Using Bash Script (Linux/Mac)

```bash
# Navigate to your project directory
cd /path/to/india-grants-oracle

# Make script executable and run
chmod +x scripts/setup-github.sh
./scripts/setup-github.sh
```

## 🔧 Manual Setup

If you prefer to set up manually or the automated scripts don't work:

### Step 1: Initialize Git Repository

```bash
# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: India Grants Oracle - Multi-agent grant discovery system"
```

### Step 2: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `india-grants-oracle`
3. Description: `One source-of-truth for every non-dilutive rupee the Indian government offers startups`
4. Make it **Public**
5. **Don't** initialize with README (we already have one)
6. Click "Create repository"

### Step 3: Connect and Push

```bash
# Add remote origin
git remote add origin https://github.com/YOUR_USERNAME/india-grants-oracle.git

# Set main branch
git branch -M main

# Push to GitHub
git push -u origin main
```

### Step 4: Update README

Edit the `README.md` file and replace `YOUR_USERNAME` with your actual GitHub username in the clone URL.

```bash
# Commit the updated README
git add README.md
git commit -m "Update README with correct repository URL"
git push
```

## 🔐 Setting Up GitHub Secrets

After creating the repository, set up environment variables for CI/CD:

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add the following secrets:

### Required Secrets

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | `sk-...` |
| `DATABASE_URL` | Database connection string | `postgresql://...` |
| `SLACK_WEBHOOK_URL` | Slack webhook URL | `https://hooks.slack.com/...` |

### Optional Secrets

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `TWILIO_SID` | Twilio Account SID | `AC...` |
| `TWILIO_TOKEN` | Twilio Auth Token | `...` |
| `REDIS_URL` | Redis connection string | `redis://...` |

## 🏗️ Repository Structure

Your repository will include:

```
india-grants-oracle/
├── src/                    # Source code
│   ├── agents/            # AI orchestrators
│   ├── scrapers/          # Web scrapers
│   ├── database/          # Database models
│   ├── api/              # Flask API
│   └── notifications/    # Notification systems
├── tests/                 # Test files
├── scripts/               # Setup and utility scripts
├── terraform/            # Infrastructure as code
├── docs/                 # Documentation
├── .github/              # GitHub Actions workflows
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Multi-service setup
├── README.md             # Project documentation
└── LICENSE               # MIT License
```

## 🚀 CI/CD Pipeline

The repository includes GitHub Actions workflows for:

- **Testing**: Run tests on every push and pull request
- **Linting**: Code quality checks with flake8 and black
- **Docker Build**: Build and test Docker images
- **Deployment**: Automatic deployment (configurable)

### Workflow Files

- `.github/workflows/ci.yml` - Main CI/CD pipeline
- `.github/workflows/deploy.yml` - Deployment workflow (customize as needed)

## 📊 Repository Features

### 🏷️ Topics and Labels

Add these topics to your repository for better discoverability:

- `python`
- `ai`
- `grants`
- `startups`
- `india`
- `government`
- `api`
- `machine-learning`
- `web-scraping`
- `flask`
- `postgresql`

### 📝 Repository Description

```
One source-of-truth for every non-dilutive rupee the Indian government offers startups (₹10k → ₹25 Cr)

A comprehensive multi-agent system that discovers, tracks, and notifies about government grants, subsidies, and funding schemes for Indian startups using AI-powered web scraping and intelligent data extraction.
```

## 🔗 Social Links

Add these to your repository settings:

- **Website**: `https://github.com/YOUR_USERNAME/india-grants-oracle`
- **Topics**: `python, ai, grants, startups, india, government, api`

## 📈 Analytics and Insights

After publishing, you can track:

- **Traffic**: Views, clones, downloads
- **Contributors**: Code contributions
- **Issues**: Bug reports and feature requests
- **Pull Requests**: Community contributions

## 🤝 Community Guidelines

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Issue Templates

Create issue templates for:
- Bug reports
- Feature requests
- Documentation improvements
- Security vulnerabilities

## 🔒 Security

### Branch Protection

Enable branch protection for `main`:
1. Go to Settings → Branches
2. Add rule for `main` branch
3. Enable:
   - Require pull request reviews
   - Require status checks to pass
   - Require branches to be up to date

### Security Alerts

GitHub will automatically scan for:
- Known vulnerabilities in dependencies
- Secret leaks in code
- Security policy compliance

## 📚 Documentation

### Wiki Setup

Consider creating a wiki for:
- Detailed setup instructions
- API documentation
- Troubleshooting guides
- FAQ

### GitHub Pages

Enable GitHub Pages for:
- Live documentation
- API documentation
- Project showcase

## 🎉 Next Steps

After setting up your repository:

1. **Share**: Share the repository URL with your network
2. **Star**: Star the repository to show support
3. **Watch**: Watch for updates and issues
4. **Contribute**: Start working on features and improvements
5. **Deploy**: Set up deployment to your preferred platform

## 🆘 Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Use GitHub CLI: `gh auth login`
   - Or use personal access token

2. **Push Rejected**
   - Pull latest changes: `git pull origin main`
   - Resolve conflicts if any

3. **CI/CD Failures**
   - Check GitHub Actions logs
   - Verify secrets are set correctly
   - Ensure all dependencies are in requirements.txt

### Getting Help

- **GitHub Issues**: Create an issue for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Check README.md and other docs
- **Community**: Join relevant GitHub communities

---

**🎯 Your India Grants Oracle repository is now ready to help Indian startups discover government funding opportunities!** 