# Use a minimal Python 3.10 image
FROM python:3.10-slim

# Set working directory
WORKDIR /code

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all source files
COPY . .

# Expose port required by Hugging Face
ENV PYTHONPATH=/code
EXPOSE 7860

# Run your main app file
CMD ["python", "main.py"]
