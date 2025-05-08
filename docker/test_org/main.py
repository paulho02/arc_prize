import torch

# Check if CUDA is available
print("CUDA Available:", torch.cuda.is_available())

# Get the name of the GPU
if torch.cuda.is_available():
    print("GPU Name:", torch.cuda.get_device_name(0))
    print("Memory Allocated:", torch.cuda.memory_allocated(0) / 1024**3, "GB")
    print("Memory Reserved:", torch.cuda.memory_reserved(0) / 1024**3, "GB")
else:
    print("No GPU detected.")