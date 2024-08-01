# Base image
FROM python:3.12

# Set the working directory in the container
WORKDIR /app

# Copy requirements and install dependencies
COPY backend/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY backend/ /app/backend/
COPY frontend/ /app/frontend/

# Expose port 8000
EXPOSE 8000

# Copy entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Define entrypoint to run migrations and start server
ENTRYPOINT ["/app/entrypoint.sh"]


# # Base image
# FROM python:3.12

# # Set the working directory in the container
# WORKDIR /app

# # Copy requirements and install dependencies
# COPY backend/requirements.txt /app/
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy project files
# COPY backend/ /app/
# COPY frontend/ /app/frontend/

# # Collect static files and apply database migrations
# RUN python manage.py collectstatic --noinput && \
#     python manage.py makemigrations && \
#     python manage.py migrate

# EXPOSE 8000
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
