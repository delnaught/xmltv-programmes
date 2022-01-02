FROM python:3

ADD entrypoint.py /entrypoint.py
ADD xslt /

RUN python -m pip install --upgrade pip \
    && python -m pip install -r requirements.txt

ENTRYPOINT ["python", "/entrypoint.py"]
