FROM python:3

ADD . /repo
WORKDIR /repo
RUN pip3 install .
RUN rm -rf /repo

CMD [ "operator-courier", "--help"]
