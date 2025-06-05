# syntax=docker/dockerfile:1

FROM python:3.13

COPY . /usr/src/app

WORKDIR /usr/src/app

RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 80

CMD ["/bin/bash", "-c", "/usr/src/app/.venv/bin/python3 /usr/src/app/.venv/bin/flask run -h 0.0.0.0 -p 80"]