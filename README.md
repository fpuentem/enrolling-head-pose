# enrolling-head-pose
Head pose stimation and snapshots for further processing in enrolling system.

$ docker buil -f jetson.Dockerfile -t "vt enrolling-head-pose:latest-jetson-xavier" .

$ docker run -it -d -p 0.0.0.0:5000:5000 vt enrolling-head-pose:latest-jetson-xavier