FROM python:3.10-slim

WORKDIR /code

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Set env to writable location WITH the expected folder name
ENV PYTHONPATH=/code
ENV DEEPEVAL_CACHE_DIR=/code/.deepeval

# Pre-create the folder to avoid permission errors
RUN mkdir -p /code/.deepeval

EXPOSE 7860
CMD ["python", "main.py"]
