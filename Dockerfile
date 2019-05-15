FROM ubuntu:18.04

WORKDIR /app

RUN apt-get update -y && apt-get install -y python3 python3-pip

COPY ./requirements.txt ./

RUN pip3 install -r requirements.txt

COPY . .

CMD python3 app.py
