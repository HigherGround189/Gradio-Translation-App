# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 7860 available to the world outside this container
EXPOSE 7860

# Define environment variable to ensure Gradio listens on all network interfaces
ENV GRADIO_SERVER_NAME=0.0.0.0

# Run app.py when the container launches
CMD ["python", "main.py"]
