FROM python:3.12-slim

# Configures settings for the image.
WORKDIR /app

# Installs your dependencies.
RUN pip install -U pip
RUN pip install uv
COPY requirements.txt .
RUN uv pip install --system --no-cache-dir -r requirements.txt

# Copies your source files.
COPY src .

# Starts your model server.
CMD uvicorn marian_server:app --port 5004 --host 0.0.0.0