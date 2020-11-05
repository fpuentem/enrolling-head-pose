# docker can be installed on the dev board following these instructions:
# https://docs.docker.com/install/linux/docker-ce/debian/#install-using-the-repository , step 4: arm64
# 1) build: docker build -f jetson-nano.Dockerfile -t "neuralet/smart-social-distancing:latest-jetson-nano" .
# 2) run: docker run -it --runtime nvidia --privileged -p HOST_PORT:8000 -v "$PWD/data":/repo/data neuralet/smart-social-distancing:latest-jetson-nano

FROM nvcr.io/nvidia/l4t-base:r32.3.1


# The `python3-opencv` package is old and doesn't support gstreamer video writer on Debian. So we need to manually build opencv.
ARG OPENCV_VERSION=4.3.0
# http://amritamaz.net/blog/opencv-config
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        cmake \
        curl \
        git \
        gstreamer1.0-plugins-bad \
        gstreamer1.0-plugins-good \
        gstreamer1.0-plugins-ugly \
        gstreamer1.0-vaapi \
        libavcodec-dev \
        libavformat-dev \
        libgstreamer-plugins-base1.0-dev \
        libgstreamer1.0-dev \
        libsm6 \
        libswscale-dev \
        libxext6 \
        libxrender-dev \
        mesa-va-drivers \
        python3-dev \
        python3-numpy \
    && rm -rf /var/lib/apt/lists/* \
    && cd /tmp/ \
    && curl -L https://github.com/opencv/opencv/archive/${OPENCV_VERSION}.tar.gz -o opencv.tar.gz \
    && tar zxvf opencv.tar.gz && rm opencv.tar.gz \
    && cd /tmp/opencv-${OPENCV_VERSION} \
    && mkdir build \
    && cd build \
    && cmake \
        -DBUILD_opencv_python3=yes \
        -DPYTHON_EXECUTABLE=$(which python3) \
        -DCMAKE_BUILD_TYPE=RELEASE \
        -DBUILD_TESTS=OFF \
        -DBUILD_PERF_TESTS=OFF \
        -DBUILD_EXAMPLES=OFF \
        -DINSTALL_TESTS=OFF \
        -DBUILD_opencv_apps=OFF \
        -DBUILD_DOCS=OFF \
        ../ \
    && make -j$(nproc) \
    && make install \
    && cd /tmp \
    && rm -rf opencv-${OPENCV_VERSION} \
    && apt-get purge -y \
        cmake \
        git \
        libgstreamer-plugins-base1.0-dev \
        libgstreamer1.0-dev \
        libxrender-dev \
    && apt-get autoremove -y

# https://askubuntu.com/questions/909277/avoiding-user-interaction-with-tzdata-when-installing-certbot-in-a-docker-contai
ARG DEBIAN_FRONTEND=noninteractive

COPY ./requirements.txt /

# Installing other modules of python
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        # tzdata \
        # libboost-python-dev \
        # libboost-thread-dev \
        pkg-config \
        python3-dev \
        python3-matplotlib \
        python3-numpy \
        python3-pillow \
        python3-pip \
        python3-scipy \
        python3-wget \
    && pip3 install -r requirements.txt \
    && pip3 install imutils \
    && apt-get purge -y \
        pkg-config \
    && apt-get autoremove -y

COPY . /repo/
WORKDIR /repo
ENTRYPOINT ["bash", "start_services.bash"]

