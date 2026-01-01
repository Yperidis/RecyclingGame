# Introduction
This is an application developed in Python with the [Otree](https://www.otree.org/) framework implementing an online experiment on a proof of concept about the feasibility of decentralized solid waste management through a digital platform.


# Setup

## Prerequisites
The project has been developed, tested and deployed with the following OS, python version and additional python packages: 
* Ubuntu 20.04
* Python 3.8.3
* Otree 5.7.2

## Otree Installation
The code can be installed via [pip](https://pypi.org/project/pip/) as per the instructions in the Otree page
(`pip install otree`).

## Run Locally
Type `otree devserver` from a terminal in the parent directory and then open the provided URL. Follow the prompts of the GUI to test the experiment locally.

## Docker Setup
To run the whole project through a docker container you will need to install [docker](https://docs.docker.com/engine/install/).

Once docker has been installed the first step would be to build the image with `docker build -t otree-app .`.

Then you can run the server locally via `docker run -it -p 8000:8000 --name otree-container otree-app` (specifying port 8000 as the server's output). Note that this is a development instance and should **not be used for production**.

Finally, open the app on your browser at `http://localhost:8000`.

# How to cite this code
If you use this code in your research or find it useful please cite this repository.