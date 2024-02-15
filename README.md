# takehome

When running application in Docker:
1. Ensure that port 8000 is unused as this is the port set in docker-compose.yml.
2. See to it that you are running in main directory (Ex. C:\take-home).
3. In the command line, enter 'docker-compose up -d' to create your Docker image and environment inside your Docker container.
4. If you are unable to query, run these commands to push changes to your SQLite db:

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
