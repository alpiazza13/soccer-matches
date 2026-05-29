# Soccer Match Tracker - Production Cloud Architecture & Deployment Guide

This document outlines the production deployment strategy and serverless architecture for the Soccer Match Tracker application. The system uses a serverless multi-cloud architecture optimized for professional career development, maintaining a **$0/month** structural baseline by fully leveraging cloud free-tiers.

## 1. Core Stack & Cost Profile

By implementing a multi-cloud strategy, the database remains entirely free indefinitely, avoiding the standard 12-month expiration limits common with traditional cloud relational databases.

Technology | Role in Architecture | Cost Profile
--- | --- | ---
**AWS Amplify** | Hosts Next.js frontend edge assets. Pulls from GitHub to compile builds, manages SSL/TLS certificates, and provisions edge CDN routing. | $0/month (Free Tier covers 1,000 build minutes, 500,000 requests, and 15 GB data transfer per month). Custom domain mapping is free.
**Porkbun** | Domain Name Registrar providing the custom web address endpoint (`matchesqueue.com`). Points authoritative nameservers to AWS. | $11.00/year (Flat annual registration pass; auto-renew can be disabled to prevent recurring subscription loops).
**AWS Route 53** | Managed Domain Name System (DNS) service. Hosts the public zone for `matchesqueue.com`, routing traffic from the apex domain to the Amplify deployment and handling subdomain aliases. | $0.50/month per hosted zone + $0.40 per million queries (negligible under portfolio traffic volumes).
**AWS Lambda** | Executes the Python FastAPI backend and background data synchronization worker. Run-times scale to zero immediately when idle. | $0/month (Permanent Always-Free Tier covers 1 Million invocations and 400,000 GB-seconds of compute capacity monthly).
**AWS API Gateway** | Acts as the public reverse-proxy traffic controller routing frontend fetches down to the active API Lambda. | $0/month for the first 12 months (1 Million requests/month). Post-free tier transitions to a negligible $1.00 per 1 million requests.
**Supabase** | Holds the cloud transactional data layer (PostgreSQL). | $0/month Permanent Free Tier (Supports data volumes up to 500 MB, accommodating years of match tracker records).
## 2. Docker Integration

### What is Docker?

Docker is an industry-standard containerization platform that encapsulates application source code alongside its exact system dependencies, operating system libraries, and environmental binaries into a single portable artifact called a **Container Image**.

### Why We Are Using It

- **Eliminates Environment Drift:** Guarantees that the backend runs identically on a local development machine or inside the AWS Linux micro-runtime environment.
    
- **Simplifies Lambda Deployment:** Native AWS Lambda zip-file deployments complicate binary compilation for third-party C-extensions like PostgreSQL adapters. Wrapping FastAPI into an official AWS Python base Docker image standardizes dependencies smoothly.
    
- **High-Value Career Skill:** Designing and pushing production-grade containerized images to services like AWS ECR (Elastic Container Registry) is a foundational skill for modern Cloud and DevOps Engineer roles.
    

## 3. AWS Components & Their Roles

- **IAM (Identity and Access Management)**
    
    - **What it is:** AWS's identity, access control, and security service.
        
    - **Application:** Secures local deployments via a dedicated IAM user with programmatic keys to avoid using the Root Account. Uses IAM roles to explicitly grant the API Lambda permission to invoke the Sync Worker Lambda.
        
- **ECR (Elastic Container Registry)**
    
    - **What it is:** A managed container image registry service.
        
    - **Application:** Serves as the secure cloud repository for backend Docker images, ensuring that the cloud application runs with the exact same dependencies compiled locally.
- **AWS Lambda**

	- **What it is:** An event-driven, serverless computing platform that automatically scales compute resources to match incoming traffic volumes exactly.
	    
	- **Application:** Houses our containerized FastAPI web application (`soccer-match-tracker-api`) and our automated background ingestion script (`soccer-match-tracker-sync-worker`) inside lightweight, cost-isolated micro-environments.
- **API Gateway**
    
    - **What it is:** A fully managed service that makes it easy to create, publish, maintain, and secure APIs at scale.
        
    - **Application:** Catches HTTP requests from the frontend and routes them to the API Lambda. Configured with global throttling limits (Rate: 10/sec, Burst: 20) to protect the database from connection crashes and insulate the account from billing spikes.
    - When a user interacts with your app, the network flow works like this:
		1. The frontend sends an HTTP request to your public **API Gateway** URL.
		    
		2. API Gateway packages that request into a JSON object and passes it to the **`soccer-match-tracker-api` Lambda function**.
		    
		3. Inside that Lambda function, an adapter called **Mangum** translates that JSON object into a format your **FastAPI application** understands.
		    
		4. FastAPI reads the URL path (like `/api/matches`), finds the corresponding function in your code, runs it, and sends the response back up the chain.
		
		API Gateway provides the public web address and the security guardrails, while your Lambda contains the actual FastAPI code that decides what data to return.
- 
**Amazon EventBridge**

	- **What it is:** A serverless routing engine that coordinates automated tasks and data flows across the cloud environment.
	    
	- **Application:** Manages our automated execution schedules, triggering the background Sync Worker exactly once every hour without human intervention.
				
- **AWS Amplify**
    
    - **What it is:** A set of purpose-built tools and features to deploy secure, scalable full-stack applications.
        
    - **Application:** Hosts the Next.js frontend, connecting directly to the repository to build and provision the required Server-Side Rendering (SSR) environment while serving edge assets via a CDN loop.
    
    - **Domain Association:** Within the Amplify console, you explicitly associate your domain (`matchesqueue.com`) with your application. This triggers Amplify to automatically provision an **SSL/TLS certificate** via AWS Certificate Manager (ACM) and configure the environment to listen for traffic coming from your root domain, routing it directly to your production deployment branch (the "main" branch).
    
- **Route 53**
	
	- **What it is:** A highly available and scalable cloud Domain Name System (DNS) web service.
	
	- **Application:** Manages a **Hosted Zone** that acts as the authoritative nameserver  for your domain. It delegates incoming traffic to your AWS resources and enables professional management of the root domain apex (the simplest version of your web address, e.g., `matchesqueue.com`) through AWS’s native infrastructure.
		- What is an authoritative nameserver?
		    - Think of this as the "Source of Truth" for your domain. When someone types `matchesqueue.com` into their browser, their computer asks a series of servers (resolvers) where to find that website. Eventually, that query reaches your **Authoritative Nameserver** (the one managed by Route 53).
		    
			- This server is "authoritative" because it holds the final, official DNS records for your domain. It doesn't just guess or ask someone else; it knows exactly which IP address or AWS resource corresponds to your website. If you update a record here, it becomes the official global record for your domain.
			
	- **Linking to Amplify:** Route 53 is linked to the AWS Amplify distribution via an **Alias record**. This acts as a direct pointer, mapping your root domain (`matchesqueue.com`) and your `www` subdomain to your Amplify-generated content delivery network (CDN) endpoint. This ensures that when a user types your URL, the DNS query resolves instantly to the exact infrastructure hosting your Next.js application.
	
- **AWS Shield Standard**

	-  **What it is:** A free, automatically enabled managed service that provides protection against Distributed Denial of Service (DDoS) attacks for applications running on AWS.
	
	- **Application:** Automatically enabled by default to protect public-facing resources like the Route 53 hosted zone, API Gateway, and Amplify distributions by detecting and mitigating anomalous traffic patterns at the network edge.
        
## 4. Data Sync Automation & Decoupled Compute Pattern

### The Serverless Background Task Challenge

In traditional, monolithic server architectures, data ingestion routines run as continuous, persistent background workers (e.g., Celery, Redis queues, or local system cron jobs). However, in an event-driven serverless ecosystem like AWS Lambda, functions are inherently ephemeral. They are designed to spin up instantly to handle an event, execute immediately, and terminate. Keeping a web API handler open for long periods to perform heavy data processing triggers steep execution timeout penalties, degrades user experience, and causes connection failures.

### The Solution: Decoupled Ingestion via Isolated Compute

To resolve these restrictions, the runtime architecture splits synchronization responsibilities across two completely isolated compute environments:

1. **Web App Lambda (`soccer-match-tracker-api`):** Configured exclusively to handle incoming web endpoints (e.g., user authentication, dashboard fetching, and match monitoring) instantly. It is optimized for ultra-fast startup execution speeds and shuts down immediately when idle.
    
2. **Sync Worker Lambda (`soccer-match-tracker-sync-worker`):** A completely standalone execution environment containing only our database synchronization script entry point (`sync_db.py`). Because it is physically isolated from the user-facing web API, we can safely allocate it an extended execution timeout ceiling (5 minutes) and dedicated error-handling logic.
    

### Dual Ingestion Triggers (Automated vs. Manual)

The `sync-worker` is structurally decoupled so that it can be invoked independently by two entirely distinct event sources:

- **Automated Schedule (Amazon EventBridge):** A native AWS serverless event bus service configured with a fixed schedule expression: `cron(0 * * * ? *)`. At the top of every hour, EventBridge automatically broadcasts a scheduled invocation event payload directly to the Sync Worker Lambda to ingest the latest data.
    
- **Manual Trigger (Frontend "Refresh Data" Button):** When a user triggers an on-demand sync from the client UI, the frontend issues a request that offloads the execution to the `sync-worker` rather than processing the data sync within the main API Lambda itself.
    

### Why Manual Sync Must Offload to the Sync-Worker

- **API Gateway Hard Timeout (29-Second Limit):** AWS API Gateway enforces a strict, unchangeable execution ceiling of 29 seconds. Because fetching external sports APIs and processing bulk database upserts can easily exceed this window, running the sync directly inside the main web API Lambda would cause API Gateway to abruptly sever the connection and throw a `504 Gateway Timeout` error to the frontend.
    
- **Non-Blocking User Experience (`202 Accepted`):** By routing the manual refresh event to the `sync-worker` asynchronously, the Web App Lambda can instantly return an HTTP `202 Accepted` status code back to the client. This allows the frontend UI to immediately display a "Syncing in progress..." status indicator to the user without locking up the browser tab or blocking other API traffic, while the worker handles the heavy data processing safely in the background using its generous 5-minute timeout.

## 5. External Components

- **Supabase (PostgreSQL)**
    
    - **What it is:** An open-source Firebase alternative providing a fully managed cloud Postgres database.
        
    - **Application:** Acts as the cloud transactional data layer, storing tables for user credentials, teams, competitions, and match synchronization metadata.
        

## 6. Deployment Workflow

Because the backend relies on system-level binaries (like PostgreSQL database adapters), the deployment pipeline uses containerization to eliminate environment drift.

1. **Build:** Compile the backend application into a local Docker container image targeted specifically for ARM64 architecture.
    
2. **Tag:** Label the local container image with the specific AWS ECR repository URI.
    
3. **Push:** Authenticate the local Docker client with AWS using the CLI, then upload the container up to the cloud repository.
    
4. **Redeploy:** Instruct the targeted Lambda functions via the AWS Console or CLI to deploy the newly updated `:latest` image from ECR.




