# syntax=docker/dockerfile:1
FROM python:3.9
WORKDIR /code
ENV JSON_DEBUG=True
ENV JSON_DATABASE=baza_wiedzy.json
COPY requirements.txt requirements.txt
COPY main_api.py main_api.py
COPY baza_wiedzy.json baza_wiedzy.json
RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["python", "main_api.py"]

