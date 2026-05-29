1. **From your backend directory, compile your backend into a local Docker container image:**
    
    Bash
    
    ```
    docker build --platform linux/arm64 --provenance=false --sbom=false -t soccer-matches-backend .
    ```
    
    _(Make sure the tiny period `.` is at the very end of the command—it tells Docker to look at your current folder)._
    
2. **Tag your newly built local container so it knows exactly which AWS repository it belongs to:**
    
    Bash
    
    ```
    docker tag soccer-matches-backend:latest 558147955096.dkr.ecr.us-east-2.amazonaws.com/soccer-match-tracker-backend:latest
    ```
    
3. **Upload (Push) the container from your laptop up into the AWS cloud registry:**
    
    Bash
    
    ```
    docker push 558147955096.dkr.ecr.us-east-2.amazonaws.com/soccer-match-tracker-backend:latest
    ```
If 403 forbidden error occurs, run below to reauthenticate, and then run push command again:

	Bash
	
	```
	aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 558147955096.dkr.ecr.us-east-2.amazonaws.com
	```

4. Navigate to `soccer-match-tracker-api` lambda, go to **Code**, click **Deploy new image**, make sure `arm64` is selcted under **Architecture**, click **Browse images** and select latest, click **Save**. Do the same for `soccer-match-tracker-sync-worker`