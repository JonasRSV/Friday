FROM rustembedded/cross:x86_64-unknown-linux-gnu-0.2.1

WORKDIR /app
COPY ./platforms.Resources/libtensorflow-unknown-linux_x86.zip .
RUN apt-get update && apt-get install -y unzip
RUN apt-get install -y libasound2 libasound2-dev
RUN unzip libtensorflow-unknown-linux_x86.zip
RUN mv libtensorflow.so.1 /lib/x86_64-linux-gnu/libtensorflow.so
RUN mv libtensorflow_framework.so.1 /lib/x86_64-linux-gnu/libtensorflow_framework.so

RUN ldconfig

