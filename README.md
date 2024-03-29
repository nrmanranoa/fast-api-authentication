# takehome

When running application in Docker:
1. Ensure that port 8000 is unused as this is the port set in docker-compose.yml.
2. See to it that you are running in main directory (Ex. C:\take-home).
3. In the command line, enter 'docker-compose up -d' to create your Docker image and environment inside your Docker container.
4. If you are unable to query, run these commands inside your container to push changes to your SQLite db:

    alembic revision --autogenerate -m "message"

    alembic upgrade head

When running application using venv:
1. Ensure that port 8000 is unused as this is the default port for running FastAPI in your local.
2. See to it that you are running in main directory (Ex. C:\take-home).
3. In the command line, enter 'pip install -r requirements.txt' to install all dependencies.
4. Before running your server, activate your venv by entering 'activate' in you command line.
5. Run this command to start your server:

    uvicorn app.main:app --reload        
6. If you are unable to query, run these commands to push changes to your SQLite db:

    alembic revision --autogenerate -m "message"

    alembic upgrade head


How the server works

1. Login

Endpoint: POST http://127.0.0.1:8000/login

Description: Logs in a user and generates an access token for authentication.

Parameters:

user_credentials: Form data containing username (email) and password.

Responses:

200 OK: Successful login. Returns an access token.

401 Unauthorized: Invalid credentials.

422 Unprocessable Entity: 

- The email address is not valid. It must have exactly one @-sign.

- Both email and password are required.

2. Create User

Endpoint: POST http://127.0.0.1:8000/users

Description: Creates a new user account.

Parameters:

user: Request body containing user details, including email and password.

Responses:

201 Created: User account created successfully. Returns user details.

409 Conflict: Email already registered.

422 Unprocessable Entity: 

- The email address is not valid. It must have exactly one @-sign.

- Both email and password are required.

- The password policy requires a minimum length of 8 characters and at least one lowercase letter, one uppercase letter, and one digit.