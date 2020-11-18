# enrolling-head-pose
Head pose stimation and snapshots for further processing in enrolling system.

$ docker buil -f jetson.Dockerfile -t "vt/enrolling-head-pose:latest-jetson-xavier" .

$ docker run -it -d -p 0.0.0.0:5000:5000 vt/enrolling-head-pose:latest-jetson-xavier

# For other docker 
$ docker run -it --volumes-from 6d0c328cbf56 nvcr.io/nvidia/l4t-base:r32.3.1 /bin/bash

# Enrolling
docker run --device /dev/video0 -v /repo/pictures -it -d -p 0.0.0.0:5000:5000 vt/enrolling-head-pose:latest-jetson-xavier
