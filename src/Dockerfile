# Use official Python image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy the requirements file from the root
COPY ../requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the src folder contents
COPY . .

# Expose Flask port
EXPOSE 5000

# Launch Flask app
CMD ["python", "app.py"]

