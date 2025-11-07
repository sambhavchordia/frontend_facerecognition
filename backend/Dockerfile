# Use a standard, slim Python base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies required by OpenCV
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
&& rm -rf /var/lib/apt/lists/*

# --- THIS IS THE FIX ---
# Copy the requirements file from the 'backend' subfolder
COPY backend/requirements.txt .

# Install your Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# --- THIS IS THE FIX ---
# Copy *only* the backend application code into the container
COPY backend/ .

# Run Gunicorn (which is in your requirements.txt) on port 7860
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:7860"]