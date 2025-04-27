# mount_dir='/home/paul02/Documents/kaggle_arc_prize'

# sudo docker run -it --cap-add=SYS_PTRACE --security-opt seccomp=unconfined \
# --device=/dev/kfd --device=/dev/dri --group-add video \
# --ipc=host --shm-size 8G \
# -v "${mount_dir}:/working_dir" \
# -w /working_dir \
# rocm/pytorch:latest

mount_dir='/home/paul02/Documents/kaggle_arc_prize'

docker run -it --cap-add=SYS_PTRACE --security-opt seccomp=unconfined \
--device=/dev/kfd --device=/dev/dri --group-add video \
--ipc=host --shm-size 8G \
-v "${mount_dir}:/working_dir" \
-w /working_dir \
-d \
rocm/pytorch