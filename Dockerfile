# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container at /app
COPY . .

# Make port 8501 available to the world outside this container
# Streamlit's default port is 8501
EXPOSE 8501

# Define environment variables for API keys (optional, can be set at runtime)
# ENV OPENWEATHER_API_KEY YOUR_OPENWEATHER_API_KEY_HERE
# ENV GOOGLE_API_KEY YOUR_GOOGLE_API_KEY_HERE

# Run app.py when the container launches using streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]