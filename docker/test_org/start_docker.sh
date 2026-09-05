#!/usr/bin/env bash
# Launch the ROCm PyTorch container with the repository mounted at /working_dir.
# Override the mount point with:  MOUNT_DIR=/path/to/repo ./start_docker.sh
mount_dir="${MOUNT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"

docker run -it --cap-add=SYS_PTRACE --security-opt seccomp=unconfined \
--device=/dev/kfd --device=/dev/dri --group-add video \
--ipc=host --shm-size 8G \
-v "${mount_dir}:/working_dir" \
-w /working_dir \
-d \
rocm/pytorch
