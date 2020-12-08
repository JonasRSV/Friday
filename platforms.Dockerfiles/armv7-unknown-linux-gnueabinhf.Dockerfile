FROM rustembedded/cross:armv7-unknown-linux-gnueabihf-0.2.1

WORKDIR /app
COPY ./platforms.Resources/libtensorflow-unknown-linux-pi32.zip .
RUN apt-get update && apt-get install -y unzip

RUN dpkg --add-architecture armhf
RUN apt-get update

RUN apt-get install --assume-yes -y libasound2:armhf libasound2-dev:armhf 
RUN unzip libtensorflow-unknown-linux-pi32.zip

RUN mv libtensorflow.so /lib/libtensorflow.so
RUN mv libtensorflow_framework.so /lib/libtensorflow_framework.so

RUN ldconfig

ENV PKG_CONFIG_LIBDIR=/usr/local/lib/arm-linux-gnueabihf/pkgconfig:/usr/lib/arm-linux-gnueabihf/pkgconfig

