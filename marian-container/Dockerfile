FROM python:3.12-slim

# Configures settings for the image.
WORKDIR /app

# Installs your dependencies.
RUN pip install -U pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copies your source files.
COPY src .

# Starts your model server.
CMD uvicorn marian_server:app --port 5003 --host 0.0.0.0