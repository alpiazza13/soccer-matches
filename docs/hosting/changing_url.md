# Domain Configuration Guide (Porkbun + AWS Route 53)

### Step 1: Purchase the Domain via Porkbun

1. Go to **Porkbun.com** and purchase your desired domain name.
    
2. Keep the Porkbun dashboard open once the transaction completes.
    

### Step 2: Create an AWS Route 53 Hosted Zone

1. Log into the **AWS Console** and navigate to **Route 53**.
    
2. Click **Hosted zones** in the left sidebar, then click **Create hosted zone**.
    
3. Enter your exact domain name (e.g., `yourdomain.com`) into the Domain name field.
    
4. Set the Type to **Public hosted zone** and click **Create hosted zone**.
    

### Step 3: Delegate Authority to AWS Nameservers

1. Inside your new AWS Hosted Zone record table, locate the row assigned the **NS (Name Server)** type.
    
2. Copy the **4 unique server strings** listed in the value column (e.g., `ns-123.awsdns-24.com.`).
    
3. Switch back to your **Porkbun Domain Management** dashboard.
    
4. Locate your domain, open the **Details** dropdown, and click **Edit** next to **Nameservers**.
    
5. Erase the default Porkbun nameservers and paste in the **4 AWS Name Server strings** you copied. _(Note: Remove the trailing period `.` from the very end of each AWS string)._
    
6. Save the changes.
    

### Step 4: Map the Domain in AWS Amplify

1. Navigate to the **AWS Amplify** console and select your app.
    
2. Click **Custom domains** under Hosting in the left sidebar.
    
3. Click **Add domain** in the top-right corner.
    
4. Choose your domain from the dropdown menu and click **Configure domain**.
    
5. Leave the default subdomain mapping options as they are (`yourdomain.com` points to `main`, and `www.yourdomain.com` handles the redirect) and click **Save**.
6. Check the box for `Setup redirect from https://matchesqueue.com to https://www.matchesqueue.com`
    
7. Allow 15–20 minutes for the SSL configuration and DNS verification to finish until the status updates to a green **Available** badge.
    

### Step 5: Update FastAPI CORS Permissions

1. Open your backend code repository locally and navigate to `app/main.py`.
    
2. Update your `origins` list to include your new production URLs:
    
    Python
    
    ```
    origins = [
        "http://localhost:3000",
        "https://yourdomain.com",
        "https://www.yourdomain.com",
    ]
    ```
    
3. Save, commit, and push the code adjustments to GitHub.
    
4. Run your terminal deployment pipeline to push the updated container image to ECR and deploy it to your API Lambda function.