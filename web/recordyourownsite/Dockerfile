FROM python:3

#Set the working directory
WORKDIR /app

#copy all the files
COPY . .

#Install the dependencies
RUN apt-get -y update
RUN pip3 install -r requirements.txt

#Expose the required port
EXPOSE 8000

#Run the command
CMD ["python3", "server.py"]
