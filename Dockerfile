# Use an official Python runtime as a base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /bot

# Copy the current directory contents into the container at /bot
COPY . /bot

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run the bot script
CMD ["python", "./run.py"]
