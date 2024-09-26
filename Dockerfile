# Stage 1: Build stage with all dependencies
FROM python:3.11-slim AS builder

# Set working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install required dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Final lightweight image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy only the necessary files from the builder stage
COPY --from=builder /app /app

# Copy the app code
COPY . /app

# Expose the port and run the app
EXPOSE 5000
# Define environment variable
ENV FLASK_APP=main.py

CMD ["flask", "run", "--host=0.0.0.0"]


