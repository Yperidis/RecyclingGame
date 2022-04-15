FROM Ubuntu:20.04

RUN apt-get -y update && apt-get install python3-pip git 
RUN pip install otree
RUN python3 -m venv venv_otree
RUN source ~/venv_otree/bin/activate

RUN pip --no-cache-dir install -U pip

COPY requirements.txt .

RUN pip --no-cache-dir install -r requirements.txt

RUN useradd --create-home server -s /bin/bash

COPY . /opt/source-code

ENTRYPOINT RECYCPOLY_APP=/opt/source-code otree devserver
