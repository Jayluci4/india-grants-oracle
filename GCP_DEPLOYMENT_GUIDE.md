# 🚀 India Startup Grant Oracle - GCP Deployment Guide

This guide provides step-by-step instructions to deploy the India Startup Grant Oracle to Google Cloud Platform (GCP). You will use Terraform for infrastructure provisioning and Cloud Build for application deployment to Cloud Run.

## 🎯 Overview

This deployment will set up the following GCP services:

- **Cloud SQL (PostgreSQL)**: Managed relational database for storing grant data.
- **Memorystore (Redis)**: Managed in-memory data store for caching.
- **Cloud Run**: Serverless platform for deploying the application API and background workers.
- **Cloud Build**: CI/CD service for building and deploying container images.
- **Cloud Scheduler**: For scheduling daily grant discovery tasks.
- **Secret Manager**: For securely storing sensitive information like API keys.

## 📋 Prerequisites

Before you begin, ensure you have the following:

1.  **GCP Account**: A Google Cloud Platform account with an active billing account.
2.  **GCP Project**: A GCP project where you want to deploy the application.
3.  **GitHub Account**: A GitHub account to host the application code.
4.  **Google Cloud CLI**: Installed and authenticated on your local machine.
    -   Install: `curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-linux-x86_64.tar.gz && tar -xf google-cloud-cli-linux-x86_64.tar.gz && ./google-cloud-sdk/install.sh --quiet`
    -   Authenticate: `gcloud auth login` and `gcloud auth application-default login`
    -   Set project: `gcloud config set project YOUR_PROJECT_ID`
5.  **Terraform**: Installed on your local machine.
    -   Install: Follow instructions at [https://learn.hashicorp.com/tutorials/terraform/install-cli](https://learn.hashicorp.com/tutorials/terraform/install-cli)
6.  **Docker**: Installed on your local machine (for local testing, not strictly required for GCP deployment).
7.  **Git**: Installed on your local machine.

## 🚀 Deployment Steps

Follow these steps to deploy the India Startup Grant Oracle to GCP:

### Step 1: Clone the Repository

First, clone the application code from your GitHub repository to your local machine.

```bash
git clone https://github.com/YOUR_USERNAME/india-grants-oracle.git
cd india-grants-oracle
```

### Step 2: Configure Terraform Variables

Navigate to the `terraform` directory and configure your project-specific variables.

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

Now, open `terraform.tfvars` in a text editor and fill in the required values:

-   `project_id`: Your GCP project ID.
-   `region`: The GCP region where you want to deploy (e.g., `us-central1`).
-   `db_password`: A strong password for your PostgreSQL database.

Example `terraform.tfvars`:

```terraform
project_id = "your-gcp-project-id"
region = "us-central1"
db_password = "your-very-secure-db-password"
```

### Step 3: Initialize and Apply Terraform

Run Terraform commands to provision the GCP infrastructure (Cloud SQL, Memorystore, etc.).

```bash
terraform init
terraform plan
terraform apply
```

Confirm the `terraform apply` by typing `yes` when prompted.

After successful application, Terraform will output important values like `database_connection_name`, `database_ip`, `redis_host`, and `redis_port`. Make a note of these values.

### Step 4: Configure Cloud Build Substitutions

Open `cloudbuild.yaml` in the root directory of your project. You will need to update the `substitutions` section with the values obtained from Terraform outputs and your specific project details.

```yaml
substitutions:
  _DB_HOST: 
  _DB_PASSWORD: 
  _REDIS_HOST: 
  _CLOUDSQL_CONNECTION_NAME: 
```

-   `_DB_HOST`: Use the `database_ip` from Terraform output.
-   `_DB_PASSWORD`: Use the `db_password` you set in `terraform.tfvars`.
-   `_REDIS_HOST`: Use the `redis_host` from Terraform output.
-   `_CLOUDSQL_CONNECTION_NAME`: Use the `database_connection_name` from Terraform output.

### Step 5: Deploy Application to Cloud Run

Now, use Cloud Build to build your Docker image and deploy it to Cloud Run. Ensure you are in the root directory of your project.

```bash
gcloud builds submit --config cloudbuild.yaml \
    --substitutions=_DB_HOST="$(terraform output -raw database_ip)",_REDIS_HOST="$(terraform output -raw redis_host)",_CLOUDSQL_CONNECTION_NAME="$(terraform output -raw database_connection_name)"
```

This command will:

1.  Build the Docker image using `Dockerfile.production`.
2.  Push the image to Container Registry.
3.  Deploy the image to Cloud Run as a new service named `grants-oracle`.

After successful deployment, Cloud Build will provide you with the URL of your Cloud Run service.

### Step 6: Initialize Database with Sample Data

Connect to your Cloud SQL PostgreSQL instance and run the `scripts/setup-database.sql` script to create tables and insert initial sample data.

```bash
gcloud sql connect grants-db --user=grants --database=grantsdb
```

Enter your `db_password` when prompted. Once connected to the `psql` prompt, run the SQL script:

```sql
\i /path/to/your/cloned/repo/scripts/setup-database.sql
```

Replace `/path/to/your/cloned/repo/` with the actual path to your project directory.

### Step 7: Configure Secrets in Secret Manager

Store your sensitive API keys (OpenAI, Slack, Twilio) in GCP Secret Manager. These secrets will be securely injected into your Cloud Run service.

```bash
gcloud secrets create openai-api-key --data-file=- <<< "your-openai-api-key"
gcloud secrets create slack-webhook --data-file=- <<< "your-slack-webhook-url"
gcloud secrets create twilio-sid --data-file=- <<< "your-twilio-sid"
gcloud secrets create twilio-token --data-file=- <<< "your-twilio-token"
```

**Note**: Replace `


your-openai-api-key`, `your-slack-webhook-url`, `your-twilio-sid`, and `your-twilio-token` with your actual values.

### Step 8: Configure Cloud Run Environment Variables

Update your Cloud Run service to use the secrets from Secret Manager and other environment variables. You can do this via the GCP Console or using the `gcloud` CLI.

**Using `gcloud` CLI:**

```bash
gcloud run services update grants-oracle \
    --region us-central1 \
    --set-env-vars=OPENAI_API_KEY=projects/$PROJECT_NUMBER/secrets/openai-api-key/versions/latest \
    --set-env-vars=SLACK_WEBHOOK=projects/$PROJECT_NUMBER/secrets/slack-webhook/versions/latest \
    --set-env-vars=TWILIO_SID=projects/$PROJECT_NUMBER/secrets/twilio-sid/versions/latest \
    --set-env-vars=TWILIO_TOKEN=projects/$PROJECT_NUMBER/secrets/twilio-token/versions/latest \
    --update-env-vars=DATABASE_URL=postgresql://grants:$(gcloud secrets versions access latest --secret=db-password --format=\


value(db_password))@$(terraform output -raw database_ip):5432/grantsdb \
    --update-env-vars=REDIS_URL=redis://$(terraform output -raw redis_host):6379
```

**Note**: Replace `us-central1` with your chosen region. You will need to get your project number using `gcloud projects describe YOUR_PROJECT_ID --format="value(projectNumber)"`.

### Step 9: Configure Cloud Scheduler for Daily Tasks

Cloud Scheduler will trigger your daily grant discovery tasks. The Terraform configuration already includes a Cloud Scheduler job. You just need to ensure the Cloud Run service has the necessary permissions to be invoked by Cloud Scheduler.

1.  **Grant Invoker Role**: Grant the Cloud Scheduler service account (e.g., `service-YOUR_PROJECT_NUMBER@gcp-sa-cloudscheduler.iam.gserviceaccount.com`) the `Cloud Run Invoker` role on your `grants-oracle` Cloud Run service.

    ```bash
    gcloud run services add-iam-policy-binding grants-oracle \
        --member=serviceAccount:service-YOUR_PROJECT_NUMBER@gcp-sa-cloudscheduler.iam.gserviceaccount.com \
        --role=roles/run.invoker \
        --region=us-central1
    ```

2.  **Update Cloud Scheduler Job Target**: Ensure the Cloud Scheduler job in Terraform points to the correct Cloud Run service URL. The `cloudbuild.yaml` automatically sets the `uri` for the Cloud Scheduler job to your Cloud Run service URL.

### Step 10: Final Verification

After all steps are completed:

1.  **Access the API**: Open your Cloud Run service URL in a browser or use `curl` to verify the API endpoints are working.
2.  **Check Logs**: Monitor Cloud Run logs in GCP Logging to ensure the application is running without errors and the discovery process is being triggered by Cloud Scheduler.
3.  **Verify Data**: Check your Cloud SQL database to confirm that new grant data is being populated after scheduled discovery runs.

## 🗑️ Cleanup (Optional)

To destroy all the resources created by Terraform, navigate to the `terraform` directory and run:

```bash
terraform destroy
```

Confirm by typing `yes` when prompted.

## 📞 Support

If you encounter any issues during deployment, please refer to the GCP documentation or reach out for support.

---

**Your India Startup Grant Oracle is now permanently deployed on GCP!** 🎉

