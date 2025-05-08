# Use the existing rocm/pytorch:latest image as the base
FROM rocm/pytorch:latest

# Set the working directory
WORKDIR /working_dir

# Update package list and install dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    && apt-get clean

# Upgrade pip to the latest version
RUN pip3 install --upgrade pip

# Install the torchrl module
RUN pip3 install torchrl
RUN python3 -m pip install --upgrade 'optree>=0.13.0'
RUN python3 -m pip install --upgrade torchrl

# Ensure the installation was successful
RUN python3 -c "import torchrl; print('torchrl version:', torchrl.__version__)"

# Define the default entry point (optional)
CMD ["/bin/bash"]
