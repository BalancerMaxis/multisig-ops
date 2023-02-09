FROM python:3.9

# Set up code directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/brownie

# Install linux dependencies
RUN apt-get update \
 && apt-get install -y libssl-dev curl

## Setup node and ganache
RUN curl -fsSL https://deb.nodesource.com/setup_16.x |  bash -
RUN apt install -y nodejspwd
RUN npm install n -g \
 && npm install -g npm@latest
RUN npm install -g ganache

## Copy brownie directory
COPY . .
## Copy network config to home dir for arbitrum
RUN mkdir ~/.brownie
COPY network-config.yaml ~/.brownie/

## Install python requirements
RUN pip install -r requirements.txt

RUN apt get install bash

CMD ['/bin/bash']

