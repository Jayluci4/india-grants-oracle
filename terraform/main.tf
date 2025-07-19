terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Variables
variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "cloudsql.googleapis.com",
    "redis.googleapis.com",
    "run.googleapis.com",
    "cloudbuild.googleapis.com",
    "cloudscheduler.googleapis.com",
    "secretmanager.googleapis.com"
  ])
  
  service = each.value
  disable_on_destroy = false
}

# Cloud SQL PostgreSQL instance
resource "google_sql_database_instance" "grants_db" {
  name             = "grants-db"
  database_version = "POSTGRES_15"
  region           = var.region
  deletion_protection = false

  settings {
    tier = "db-f1-micro"
    
    backup_configuration {
      enabled = true
      start_time = "03:00"
    }
    
    ip_configuration {
      ipv4_enabled = true
      authorized_networks {
        value = "0.0.0.0/0"
        name  = "all"
      }
    }
  }
}

# Database
resource "google_sql_database" "grants_database" {
  name     = "grantsdb"
  instance = google_sql_database_instance.grants_db.name
}

# Database user
resource "google_sql_user" "grants_user" {
  name     = "grants"
  instance = google_sql_database_instance.grants_db.name
  password = var.db_password
}

# Redis instance
resource "google_redis_instance" "grants_cache" {
  name           = "grants-cache"
  memory_size_gb = 1
  region         = var.region
  tier           = "BASIC"
  redis_version  = "REDIS_7_0"
}

# Secret Manager for sensitive data
resource "google_secret_manager_secret" "openai_api_key" {
  secret_id = "openai-api-key"
  
  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret" "slack_webhook" {
  secret_id = "slack-webhook"
  
  replication {
    automatic = true
  }
}

# Cloud Scheduler job for daily discovery
resource "google_cloud_scheduler_job" "daily_discovery" {
  name     = "daily-grant-discovery"
  schedule = "0 6 * * *"  # 6 AM daily
  time_zone = "Asia/Kolkata"
  
  http_target {
    uri         = "https://grants-oracle-${random_id.suffix.hex}-uc.a.run.app/trigger-discovery"
    http_method = "POST"
    
    headers = {
      "Content-Type" = "application/json"
    }
  }
}

# Random suffix for unique naming
resource "random_id" "suffix" {
  byte_length = 4
}

# Outputs
output "database_connection_name" {
  value = google_sql_database_instance.grants_db.connection_name
}

output "database_ip" {
  value = google_sql_database_instance.grants_db.ip_address.0.ip_address
}

output "redis_host" {
  value = google_redis_instance.grants_cache.host
}

output "redis_port" {
  value = google_redis_instance.grants_cache.port
}

