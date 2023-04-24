FROM python:3.8

COPY requirements.txt ./

RUN pip3.8 install -r requirements.txt

RUN mkdir /pages && mkdir /assets && mkdir /additional_files

COPY ./additional_files/* /additional_files/
COPY ./assets/* /assets/
COPY ./pages/* /pages/
COPY ./app.py ./

WORKDIR ./

EXPOSE 8050

CMD ["python","./app.py"]