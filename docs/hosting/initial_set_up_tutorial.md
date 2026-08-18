
### Prerequisite: Install and Configure the AWS CLI

Since you are on a Mac, the absolute easiest way to install the AWS CLI is using **Homebrew**. If you don't have Homebrew, you can download the official macOS installer pkg from AWS, but let's try the terminal path first.

1. **Install the AWS CLI:** Open your terminal and run:
    
    Bash
    
    ```
    brew install awscli
    ```
    
    _(If you don't use Homebrew, download and run the macOS PKG installer directly from the official AWS CLI documentation page)._
    
2. **Verify the installation:**
    
    Bash
    
    ```
    aws --version
    ```
    
1. **Link your terminal to your AWS Account:**  (if you don't have AWS account yet, see instructions for creating one) You need to generate an **Access Key ID** and **Secret Access Key** from your AWS IAM console dashboard. Once you have them, run this command to log in locally:
    
    Bash
    
    ```
    aws configure
    ```
    
    It will prompt you for four items. Fill them out like this:
    
    - **AWS Access Key ID:** `[Paste your access key]`
        
    - **AWS Secret Access Key:** `[Paste your secret key]`
        
    - **Default region name:** `us-east-1` _(This is Northern Virginia, standard default)_
        
    - **Default output format:** `json`

### Phase 1: Environment & Code Adjustments

Before touching AWS, you need to make sure your Python codebase is ready to handle an event-driven, serverless execution context instead of a continuous local server loop.

#### Step 1.1: Install Deployment Dependencies

You need to add `mangum` to act as the ASGI adapter for AWS Lambda, alongside environment configuration helpers if you aren't using them already. Run this in your local terminal:

- `pip install mangum pydantic-settings python-dotenv`
    

Freeze your dependencies to ensure your production environment builds exactly the same way:

- `pip freeze > requirements.txt`
    

#### Step 1.2: Add Mangum to `main.py`

Open your `main.py` file. At the very bottom of the file, expose a serverless handler interface. This adapter translates incoming AWS API Gateway network payloads into standard FastAPI context items:

Python

```
from mangum import Mangum

# Standardize the Mangum handler wrapper for AWS Lambda execution
handler = Mangum(app)
```

#### Step 1.3: Externalize Configuration Settings

Ensure all secrets and structural parameters are pulled dynamically from the environment. Create a `.env.example` file in your project's root directory to serve as a checklist when configuring AWS later:

- `ENV=production`
    
- `DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres`
    
- `FOOTBALL_DATA_API_TOKEN=your_token_here`
    
- `JWT_SECRET_KEY=your_secure_secret_key`
    

### Phase 2: Create the Base Docker Image for Backend

Because Lambda functions run in a highly restricted container environment, packaging your application using an official AWS base image ensures that all system binaries (such as PostgreSQL adapters) are compiled correctly.

#### Step 2.1: Write the `Dockerfile`

Create a file named exactly `Dockerfile` (no extension) in the root directory of your project:

Dockerfile

```
FROM public.ecr.aws/lambda/python:3.11

# Copy dependency matrix
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install packages target-mapped straight into the execution directory
RUN pip install --no-cache-dir -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Copy application source modules
COPY ./app ${LAMBDA_TASK_ROOT}/app

# Command placeholder (Overridden explicitly for each Lambda function)
CMD [ "app.main.handler" ]
```

### Phase 3: Set Up AWS Container Registry (ECR)

AWS needs a secure cloud repository to host your Docker images before they can be pulled by your serverless compute functions.

#### Step 3.1: Initialize the ECR Repository via the UI

1. Open your web browser, go to **[https://aws.amazon.com](https://www.google.com/search?q=https://aws.amazon.com)**, and log in.
    
2. At the very top of the screen, you will see a large search bar. Type **ECR** into it and click on **Elastic Container Registry**.
    
3. On the ECR dashboard, look for a orange/gray button that says **Create repository** and click it.
    
4. Under **Visibility settings**, make sure **Private** is selected (this keeps your code secure and hidden from the public internet). If that's not an option, just make sure it says **Create private repository** at the top of the page.
    
5. Under **Repository name**, type exactly: `soccer-match-tracker-backend`
    
6. Scroll down to the bottom of the page, leave every other toggle completely untouched at its default setting, and click **Create repository**.
    

#### Step 3.2: Authenticate, Build, and Push via your Terminal

Now, look at the list of repositories on your screen. Click directly on the name of the repository you just created (`soccer-match-tracker-backend`).

In the top right corner of that specific repository page, click the button that says **View push commands**. AWS will pop up a window showing you 4 exact terminal commands customized with your specific AWS Account ID number.

Go to your local terminal, make sure you are in your project **backend** root folder (`soccer-matches`) where your `Dockerfile` sits, and execute the 1st command from the browser but the other three as specified below because the below verions are specified to work properly. You must already have Docker installed for this - Docker Desktop for Mac.

1. **Authenticate your local Docker app with your cloud AWS registry:**
    
    Bash
    
    ```
    aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin [YOUR_ACCOUNT_ID].dkr.ecr.us-east-1.amazonaws.com
    ```
    
    _(When you press enter, it should output a clean message saying `Login Succeeded`)_
    
2. **Compile your backend into a local Docker container image:**
    
    Bash
    
    ```
    docker build --platform linux/arm64 --provenance=false --sbom=false -t soccer-matches-backend .
    ```
    
    _(Make sure the tiny period `.` is at the very end of the command—it tells Docker to look at your current folder)._
    
3. **Tag your newly built local container so it knows exactly which AWS repository it belongs to:**
    
    Bash
    
    ```
 docker tag soccer-matches-backend:latest 558147955096.dkr.ecr.us-east-2.amazonaws.com/soccer-match-tracker-backend:latest
    ```
    
4. **Upload (Push) the container from your laptop up into the AWS cloud registry:**
    
    Bash
    
    ```
    docker push 558147955096.dkr.ecr.us-east-2.amazonaws.com/soccer-match-tracker-backend:latest
    ```
    

Once that fourth command finishes running, you will see a bunch of progress bars hit 100%. If you refresh your AWS browser window, you will see your brand new container image sitting securely in the cloud.

### Phase 4: Deploy Serverless Compute Layers

We will utilize the _same_ pushed ECR image to instantiate **two separate Lambda functions** assigned to different workloads.

#### Step 4.1: Deploy the Web API Lambda

1. Navigate to **Lambda** in the AWS console on your bowser and click **Create function**.
    
2. Select **Container image**.
    
3. Name the function `soccer-match-tracker-api`.
    
4. Click **Browse images** and select the `:latest` tag from your `soccer-match-tracker-backend` ECR repository.
5. Under **Additional settings**, toggle **ARM64 architecture** on.
    
6. Click **Create function**.
    

#### Step 4.2: Add API Configuration

1. Inside your new function, navigate to the **Configuration** tab -> **Environment variables**.
    
2. Input your production credentials (`ENV=production`, `DATABASE_URL`, `JWT_SECRET_KEY`, `FOOTBALL_DATA_API_TOKEN`).
    
3. Under **General configuration**, click **Edit**, and change the **Timeout** from 3 seconds to **30 seconds**. This accommodates database connection cold-starts so your API calls don't drop.
    

#### Step 4.3: Deploy the Sync Worker Lambda

1. Create a second function using **Container image**.
    
2. Name it `soccer-match-tracker-sync-worker`.
    
3. Select the exact same ECR image tag and other settings (ARM64 toggled on) as before.
    
4. Under **Configuration** -> **General configuration**, edit the **Timeout** to **5 minutes** (the ingestion routine performs multiple sequential API requests and needs extra execution time).

5. Add the same ENV variables as you added for the `soccer-match-tracker-api` lambda.
    
6. Under **Code** -> **Image configuration**, click **Edit**.
    
7. Override the **CMD** parameter to invoke your script entry point directly instead of the main API handler:
    
    - **CMD Override:** `app.scripts.sync_db.sync_data`
        



### Phase 5: Hook Up Routing & Automation Triggers

#### Step 5.1: Create the Public Route Gateway (API Gateway)

1. Navigate to **API Gateway** and click **Create API**.
2. Under **HTTP API** (optimized for low latency and minimal cost), click **Build**.
3. Enter `soccer-match-tracker-gateway` for the API name, select `IPv4` for **IP address type**, and click **Add Integration`
4. Select **Lambda**, and target your `soccer-match-tracker-api` function. Hit **Next**.
5. Under **Configure routes**, map the Method to `ANY` and set the Resource path to `/{proxy+}`. This forwards all wildcard sub-routing (like `/matches` or `/token`) directly to FastAPI. Select `soccer-match-tracker-api` for **Integration target**
6. Complete the wizard and copy your public invocation URL.

#### Step 5.2: Automate the Hourly Ingestion (EventBridge)

1. Navigate to **Amazon EventBridge** -> **Schedules** and click **Create schedule**.
2. Name it `hourly-soccer-data-sync`.
3. Set the schedule pattern to a standard cron rate expression: `cron(0 * * * ? *)` (this tells AWS to fire the rule exactly at the top of every hour).
4. Set the **Target** to **AWS Lambda function** and choose your `soccer-match-tracker-sync-worker`.
5. For the **Role**, choose the existing sync worker role. If not done already, update the Trust relationships of this role in the IAM Console to include `scheduler.amazonaws.com`. 
6. Click **Create**.
7. We now need to make sure the execution role for this schedule has permission to invoke the sync worker lambda function:
8. Under AmazonEventBridge --> Schedules --> `hourly-soccer-data-sync`,  go to Target and click the link to the Execution Role.
9. Click Add Permissions and paste the following into the JSON. Name the permission `EventBridgeSchedulerLambdaInvoke`
	 ```json
	 {
	"Version": "2012-10-17",
	"Statement": [
		{
			"Effect": "Allow",
			"Action": "lambda:InvokeFunction",
			"Resource": "arn:aws:lambda:us-east-2:558147955096:function:soccer-match-tracker-sync-worker"
		}
	]
}
	 ```

#### Step 5.3: Implement Front-Door Rate Limiting (Throttling)

To protect your Supabase database from connection crashes and insulate your AWS account from surprise billing, you will configure API Gateway to throttle traffic globally.

1. In the **API Gateway** console, click on your API and select **Throttling** from the left-hand menu.
    
2. Check your deployment stage is set to `$default` (in top right).
    
3. Click **Edit**
    
4. Set the following limits to ensure your app stays safely within the free tier limits while allowing normal user usage:
    
    - **Rate (Average Requests Per Second):** `10` (Allows a single user or small group of users to browse comfortably without restriction).
        
    - **Burst (Maximum Peak Requests):** `20` (Allows for brief, natural spikes when a page initial-loads multiple assets or fetches simultaneously).

### Phase 6: Frontend Mapping & CORS Alignment

This phase establishes the monorepo connection between your repository and AWS Amplify, forces the correct Server-Side Rendering (SSR) configuration, and aligns your backend security to accept traffic from your live production URL.

#### Step 6.1: Prepare the Monorepo Manifest

To ensure AWS Amplify correctly identifies your project as a **Next.js SSR** application rather than a static web site, you must create a root-level manifest.

1. Create a file named `package.json` at the absolute root of your project directory.
    
2. Paste the following content, which includes the `amplify:monorepo` instruction and the `next` dependency "bait" to trigger the correct SSR server provisioning:
    
    JSON
    
    ```
    {
      "name": "soccer-matches-monorepo",
      "version": "1.0.0",
      "private": true,
      "amplify:monorepo": {
        "appRoot": "frontend"
      },
      "dependencies": {
        "next": "16.1.1"
      }
    }
    ```
    
3. Commit and push this file to your main branch.
    

#### Step 6.2: Deploy to AWS Amplify

1. Navigate to **AWS Amplify** in the AWS Console and select **Create new app** > **Host web app**.
    
2. Authorize **GitHub**, select your repository, and choose your main branch.
    
3. On the **Build settings** page, ensure the YAML configuration is set to target the `frontend` subfolder:
    
    YAML
    
    ```
    version: 1
    applications:
      - appRoot: frontend
        frontend:
          phases:
            preBuild:
              commands:
                - npm ci
            build:
              commands:
                - npm run build
          artifacts:
            baseDirectory: .next
            files:
              - '**/*'
          cache:
            paths:
              - node_modules/**/*
    ```
    
4. In the **Environment variables** section, add your backend endpoint:
    
    - **Key:** `NEXT_PUBLIC_API_URL`
        
    - **Value:** `https://[YOUR-API-GATEWAY-ID].execute-api.us-east-2.amazonaws.com`
        
5. Click **Save and deploy**. Once complete, verify in **App settings > General** that the **Framework** is listed as **Next.js - SSR**. If it says "Web," disconnect the branch and reconnect it to force a re-scan.
    

#### Step 6.3: Align FastAPI CORS Rules

Once the deployment finishes and provides your public URL (e.g., `https://main.d123456abcdef.amplifyapp.com`), you must update your backend to allow traffic from that domain.

1. In your local backend `app/main.py`, update the `origins` list:
    
    Python
    
    ```
    origins = [
        "http://localhost:3000",
        "https://main.d123456abcdef.amplifyapp.com", # Your new production URL
    ]
    ```
    
2. Save, commit, and push your changes.
    
3. Perform your standard Docker build, tag, and push sequence to update your container in **Amazon ECR**.
    
4. Force a new deployment of your **Lambda function** so it pulls the updated image containing the new CORS policy.
    
5. Return to the Amplify console and click **Redeploy** on your app dashboard to sync the final environment state.





