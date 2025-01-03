# Use the prebuilt Selenium Chrome image
FROM selenium/standalone-chrome:latest

# Set the working directory
WORKDIR /app

# Install Python and virtual environment tools
RUN sudo apt-get update && sudo apt-get install -y python3 python3-venv python3-pip

# Create a virtual environment
RUN python3 -m venv /app/venv

# Activate the virtual environment and upgrade pip
RUN . /app/venv/bin/activate && pip install --upgrade pip

# Copy the requirements file
COPY requirements.txt .

# Install Python dependencies in the virtual environment
RUN . /app/venv/bin/activate && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Run the application using the virtual environment's Python
CMD ["/app/venv/bin/python", "main.py"]