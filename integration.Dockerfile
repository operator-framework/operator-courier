FROM operator-courier-base:latest

RUN pip3 install tox coveralls

WORKDIR /src
COPY . .
