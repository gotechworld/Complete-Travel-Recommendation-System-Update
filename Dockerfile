# Use Python 3.12 as the base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create a non-root user and group
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy the application code
COPY . .

# Create necessary directories
RUN mkdir -p .streamlit agentic

# Move files to correct locations
RUN if [ -f "interface.py" ]; then mv interface.py agentic/; fi
RUN if [ -f "workflow.py" ]; then mv workflow.py agentic/; fi
RUN touch agentic/__init__.py

# Set proper ownership
RUN chown -R appuser:appuser /app

# Expose the port Streamlit runs on
EXPOSE 8501

# Set environment variables
ENV PYTHONPATH=/app
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_HEADLESS=true

# Switch to non-root user
USER appuser

# Command to run the application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
