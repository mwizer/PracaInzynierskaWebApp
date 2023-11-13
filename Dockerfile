#
FROM python:3.10.2-bullseye

#
WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD hypercorn app:app
