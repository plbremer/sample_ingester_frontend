FROM continuumio/miniconda3

RUN mkdir /pages && mkdir /assets && mkdir /additional_files

COPY ./additional_files/* /additional_files/

COPY ./sample_ingester_frontend_min.yml /

RUN conda env create -f sample_ingester_frontend_min.yml 


COPY ./assets/* /assets/
COPY ./pages/* /pages/

COPY ./app.py ./

WORKDIR ./

EXPOSE 8050

SHELL ["conda", "run", "-n", "sample_ingester_frontend_min", "/bin/bash", "-c"]

ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "sample_ingester_frontend_min", "python", "./app.py"]