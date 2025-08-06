FROM python:3.11-slim
WORKDIR /app

# Install dependencies
COPY gypsycove/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY gypsycove/backend gypsycove/backend

# Expose the port used by the GypsyCove API
EXPOSE 8100

# Run the application using Uvicorn
CMD ["uvicorn", "gypsycove.backend.main:app", "--host", "0.0.0.0", "--port", "8100"]