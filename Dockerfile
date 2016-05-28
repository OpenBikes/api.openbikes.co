FROM python:3.5-onbuild

ADD requirements.txt /tmp/requirements.txt

RUN make install

CMD ["python"]