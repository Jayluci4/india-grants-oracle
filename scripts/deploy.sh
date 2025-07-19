#!/bin/bash

# India Startup Grant Oracle - GCP Deployment Script
set -e

echo "🏗️ Starting India Startup Grant Oracle deployment to GCP..."

# Check if required tools are installed
command -v gcloud >/dev/null 2>&1 || { echo "❌ gcloud CLI is required but not installed. Aborting." >&2; exit 1; }
command -v terraform >/dev/null 2>&1 || { echo "❌ Terraform is required but not installed. Aborting." >&2; exit 1; }

# Get project ID
PROJECT_ID=$(gcloud config get-value project)
if [ -z "$PROJECT_ID" ]; then
    echo "❌ No GCP project set. Run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo "📋 Using GCP Project: $PROJECT_ID"

# Enable required APIs
echo "🔧 Enabling required GCP APIs..."
gcloud services enable \
    cloudsql.googleapis.com \
    redis.googleapis.com \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    cloudscheduler.googleapis.com \
    secretmanager.googleapis.com

# Deploy infrastructure with Terraform
echo "🏗️ Deploying infrastructure with Terraform..."
cd terraform

# Initialize Terraform
terraform init

# Create terraform.tfvars if it doesn't exist
if [ ! -f terraform.tfvars ]; then
    echo "📝 Creating terraform.tfvars from example..."
    cp terraform.tfvars.example terraform.tfvars
    echo "⚠️  Please edit terraform.tfvars with your actual values before continuing."
    echo "   Required: project_id, region, db_password"
    read -p "Press Enter after editing terraform.tfvars..."
fi

# Plan and apply
terraform plan
read -p "🤔 Do you want to apply these changes? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    terraform apply -auto-approve
else
    echo "❌ Deployment cancelled."
    exit 1
fi

# Get outputs
DB_CONNECTION_NAME=$(terraform output -raw database_connection_name)
DB_IP=$(terraform output -raw database_ip)
REDIS_HOST=$(terraform output -raw redis_host)

cd ..

# Build and deploy application
echo "🐳 Building and deploying application..."

# Build with Cloud Build
gcloud builds submit --config cloudbuild.yaml \
    --substitutions=_DB_HOST=$DB_IP,_REDIS_HOST=$REDIS_HOST,_CLOUDSQL_CONNECTION_NAME=$DB_CONNECTION_NAME

echo "✅ Deployment completed successfully!"
echo ""
echo "📊 Your India Startup Grant Oracle is now live!"
echo "🌐 Cloud Run URL: https://grants-oracle-$(openssl rand -hex 4)-uc.a.run.app"
echo "🗄️  Database: $DB_CONNECTION_NAME"
echo "🔄 Redis: $REDIS_HOST"
echo ""
echo "🔧 Next steps:"
echo "1. Set up secrets in Secret Manager:"
echo "   gcloud secrets versions add openai-api-key --data-file=- <<< 'your-openai-key'"
echo "   gcloud secrets versions add slack-webhook --data-file=- <<< 'your-slack-webhook'"
echo "2. Initialize database with sample data"
echo "3. Configure monitoring and alerts"
echo ""
echo "📚 Check the deployment guide for detailed configuration steps."

