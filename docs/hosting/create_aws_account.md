Setting one up is straightforward, but there is one massive trap that catches a lot of developers when they create their first AWS account. Let’s make sure you bypass it completely.

### Step 1: Sign up for an AWS Account

1. Go to **[https://aws.amazon.com](https://aws.amazon.com)** and click **Create an AWS Account** in the top right corner.
    
2. Follow the prompts to enter your email address and choose an account name.
3. I selected Free Account when prompted, will just need to upgrade after 6 months but this is better for safety for now.
    
4. **Credit Card Requirement:** AWS may require you to input a credit card. Don't worry—this is purely for identity verification to prevent bot abuse. They will do a temporary $1.00 authorization charge that disappears in a few days. You are safely within the Free Tier limits for what we are building.
    
5. Choose the **Basic Support - Free** option when it asks you to select a support plan.
    

### Step 2: The Critical Security Step (Do not skip this!)

When you finish signing up and log in for the first time, you are logged in as the **Root User**.

> ⚠️ **The Trap:** Never generate AWS Access Keys for your Root Account, and never use your Root Account for daily terminal work. If a script accidentally leaks your Root Access Keys (like pushing a `.env` file to a public GitHub repo), a hacker can take over your entire billing account, lock you out, and run up a $50,000 bill mining crypto.

To protect yourself, you need to create an **IAM User** (Identity and Access Management) with restricted admin permissions just for your local machine's terminal.

Here is how to do it right:

1. Once logged into the AWS console, search for **IAM** in the top search bar and click it.
    
2. In the left sidebar, click **IAM users**, then click **Create user**.
    
3. Name the user `alex-terminal-admin` and click Next.
    
4. On the permissions page, select **Attach policies directly**.
    
5. In the search box, look for **AdministratorAccess**, check the box next to it, and click Next. _(This gives this specific user permission to build things, but keeps your main billing root account isolated)._
    
6. Click **Create user**.
    

### Step 3: Get Your Credentials

Now that your secure `alex-terminal-admin` user exists, we need to grab the keys for your terminal:

1. Click on your newly created `alex-terminal-admin` username in the user list.
    
2. Click on the **Security credentials** tab.
    
3. Scroll down to the **Access keys** section and click **Create access key**.
    
4. Select **Command Line Interface (CLI)** as your use case, check the confirmation box at the bottom, and click Next.
    
5. Click **Create access key**.
    

AWS will display your **Access Key ID** and your **Secret Access Key**.

Keep that page open! Run `aws configure` back in your Mac's terminal, paste those two keys right in,  set your region to `us-east-1`, and set you default output format to `json`

To make absolutely sure everything linked up perfectly, run this quick test command:

Bash

```
aws sts get-caller-identity
```

If it successfully returns a little block of text showing your account ID and says `alex-terminal-admin`, your terminal is officially connected to the cloud!