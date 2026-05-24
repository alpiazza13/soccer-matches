# Soccer Match Tracker - Cloud Architecture & Deployment Blueprint

This document outlines the production deployment strategy for the Soccer Match Tracker application. The design focuses on enterprise-grade patterns optimized for professional career development, while leveraging cloud free-tiers to maintain a **$0/month** structural baseline.

---

## 1. Core Stack & Cost Profile

The system uses a serverless multi-cloud architecture to ensure the database remains free indefinitely, avoiding the 12-month expiration limits of traditional cloud relational databases.

| Technology | Role in Architecture | Cost Profile |
| :--- | :--- | :--- |
| **AWS Amplify** | Hosts the Next.js frontend edge assets. Pulls directly from GitHub to compile builds and serves static resources via an S3 + CloudFront CDN loop. | **$0/month** (Free Tier covers 1,000 build minutes, 500,000 requests, and 15 GB data transfer per month). |
| **AWS Lambda** | Executes the Python FastAPI backend. Run-times spin up instantly upon an HTTP request and scale down to zero immediately when complete. | **$0/month** (Permanent **Always-Free Tier** covers 1 Million invocations and 400,000 GB-seconds of compute capacity monthly). |
| **AWS API Gateway** | Acts as the public reverse-proxy traffic controller. Routes incoming frontend client fetches down to trigger the active Lambda application loop. | **$0/month** for the first 12 months (1 Million requests/month). Post-free tier transitions to a negligible **$1.00 per 1 million requests**. |
| **Supabase** | Holds the cloud transactional data layer (PostgreSQL). Stores tables for user credentials, match tracking configurations, and synchronization metadata. | **$0/month Permanent Free Tier** (Supports data volumes up to 500 MB, which accommodates years of match tracker records). |

---

## 2. Docker Integration

### What is Docker?
Docker is an industry-standard containerization platform. It encapsulates application source code alongside its exact system dependencies, operating system libraries, and environmental binaries into a single portable artifact called a **Container Image**.

### Why We Are Using It
- **Eliminates Environment Drift:** Guarantees that the backend runs identically on your local machine, a coworker's laptop, or inside the AWS Linux micro-runtime environment.
- **Simplifies Lambda Deployment:** Native AWS Lambda zip-file deployments complicate binary compilation for third-party C-extensions (like PostgreSQL adapters). Wrapping FastAPI into an official AWS Python base Docker image standardizes dependencies smoothly.
- **High-Value Career Skill:** Designing and pushing production-grade containerized images to services like AWS ECR (Elastic Container Registry) is a foundational skill for modern Cloud and DevOps Engineer roles.

---

## 3. Data Sync Automation Pattern

### The Serverless Challenge
In our current local setup, `sync_db.py` relies on a persistent application instance or manual intervention. In an AWS Lambda ecosystem, functions are ephemeral and shut down immediately after handling a request; they cannot run continuous background loop intervals.

### The Solution: Decoupled Ingestion via EventBridge
To transition the ingestion routine to run automatically every hour without locking up our web API or creating a premium billing vector, we split the runtime responsibilities across two isolated Lambda configurations:

1. **Web App Lambda:** Dedicated exclusively to handling API Gateway endpoints (e.g., `/matches`, `/users`, `/token`).
2. **Sync Worker Lambda:** A completely standalone execution wrapper containing only our `sync_db.py` execution entry point.
3. **Amazon EventBridge (Cloud Cron):** A native AWS scheduling manager configured with a cron expression (`cron(0 * * * ? *)`). At the top of every hour, EventBridge sends a signal to wake up the **Sync Worker Lambda**, which fetches new match data, upserts it into **Supabase**, and safely tears itself down.

---

