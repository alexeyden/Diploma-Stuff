#!/bin/bash

rm -Rf opencv-3.1.0

wget https://github.com/Itseez/opencv/archive/3.1.0.zip -O opencv.zip || exit -1
unzip opencv.zip || exit -1

cd opencv-3.1.0
mkdir build
cd build

cmake -DCMAKE_BUILD_TYPE=Release \
-DBUILD_opencv_calib3d=OFF \
-DBUILD_opencv_superres=OFF \
-DBUILD_opencv_cudaimgproc=OFF \
-DBUILD_opencv_flann=OFF \
-DBUILD_opencv_java=OFF \
-DBUILD_opencv_cudafeatures2d=OFF \
-DBUILD_opencv_videoio=OFF \
-DBUILD_opencv_stitching=OFF \
-DBUILD_opencv_cudaarithm=OFF \
-DBUILD_opencv_highgui=OFF \
-DBUILD_opencv_shape=OFF \
-DBUILD_opencv_cudaobjdetect=OFF \
-DBUILD_opencv_objdetect=OFF \
-DBUILD_opencv_cudaoptflow=OFF \
-DBUILD_opencv_features2d=OFF \
-DBUILD_opencv_cudalegacy=OFF \
-DBUILD_opencv_cudev=OFF \
-DBUILD_opencv_cudacodec=OFF \
-DBUILD_opencv_photo=OFF \
-DBUILD_opencv_ml=OFF \
-DBUILD_opencv_cudabgsegm=OFF \
-DBUILD_opencv_cudawarping=OFF \
-DBUILD_opencv_cudafilters=OFF \
-DBUILD_opencv_cudastereo=OFF \
-DBUILD_opencv_ts=OFF \
-DBUILD_opencv_videostab=OFF \
-DBUILD_opencv_viz=OFF \
-DBUILD_opencv_video=OFF .. || exit -1

make -j8 || exit -1
