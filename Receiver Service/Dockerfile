FROM ubuntu:18.04
LABEL maintainer="rmatiellopletz@my.bcit.ca"
RUN apt-get update -y && \
	apt-get install -y python3 python3-pip
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip3 install -r requirements.txt
ENTRYPOINT [ "python3" ]
CMD [ "app.py" ]
