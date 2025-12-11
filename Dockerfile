# Use lightweight Python
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files
COPY . .

# Expose port
EXPOSE 8000

# Run with Uvicorn (ASGI)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]