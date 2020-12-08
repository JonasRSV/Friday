docker build -t recordyourownsite .
sudo docker run -ti -p 80:8000 -v /app/recordings:$PWD/recordings recordyourownsite
