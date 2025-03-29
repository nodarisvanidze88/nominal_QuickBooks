FROM python:3.11-slim

WORKDIR /app

# 2.1 Copy necessary files
COPY . .

# 2.2 Install requirements
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# 2.3 Check if .env exists
# RUN test -f .env || (echo ".env file is missing!" && exit 1)

# 2.4 Run Alembic migrations
# RUN alembic upgrade head

# 2.5 Run tests
# RUN pytest tests || (echo "Tests failed!" && exit 1)

# 2.6 Expose .env
# ENV ENV_FILE=.env

# 2.7 Default command for running app
CMD ["bash", "-c", "uvicorn main:app --host 0.0.0.0 --port 8000"]