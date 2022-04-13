FROM Ubuntu

RUN apt-get update && apt-get install python3-pip git 
RUN pip install otree
RUN python3 -m venv venv_otree
RUN source ~/venv_otree/bin/activate

COPY . /opt/source-code

ENTRYPOINT RECYCPOLY_APP=/opt/source-code otree devserver

