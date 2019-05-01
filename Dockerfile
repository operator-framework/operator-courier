FROM python:3

RUN pip3 install operator-courier

CMD [ "operator-courier", "--help"]
