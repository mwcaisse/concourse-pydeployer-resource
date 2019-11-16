FROM python:3.8-buster

COPY requirements.txt /opt/requirements.txt
RUN pip install -r /opt/requirements.txt

COPY ./commands/check.py /opt/resource/check
COPY ./commands/in.py /opt/resource/in
COPY ./commands/out.py /opt/resource/out

RUN chmod a+x /opt/resource/check
RUN chmod a+x /opt/resource/in
RUN chmod a+x /opt/resource/out

WORKDIR /opt/resource