notes on implementing proper user authentication, from starting point of just login by inputting email address


### Manually generating password for user

Run `hash_password('desired_password')` in security.py, manally save the result in the database. Need to run command `python -m app.utils.security` from backend directory
### Testing JWT Authentication Endpoints Locally

Go to `http://127.0.0.1:8000/docs` in your browser.

1. **Signup:** Find the `POST /users` endpoint. Click **Try it out**, enter an email and password, and hit **Execute**. You should see the user returned with a long, scrambled `hashed_password` string.
    
2. **Authorize:** Look for the green **Authorize** button at the top right of the page.
    
3. **Login:** In the popup, enter the email and password you just created. Hit **Login**.
    
    - If it works, the lock icon will close.
        
    - Behind the scenes, the browser just called your `/token` route and received the JWT.
        

If you want to see what's actually inside the token you just generated:

1. Copy the `access_token` string from the response body in Swagger.
    
2. Go to **[jwt.io](https://jwt.io)**.
    
3. Paste the token into the "Encoded" box.
    
4. On the right, you should see your email address under the `"sub"` key.