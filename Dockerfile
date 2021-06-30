# syntax=docker/dockerfile:1
FROM python:3.9
WORKDIR /code
ENV JSON_DEBUG=True
ENV JSON_DATABASE=baza_wiedzy.json
COPY requirements.txt requirements.txt
COPY main_api.py main_api.py
COPY test_main_api.py test_main_api.py
COPY baza_wiedzy.json baza_wiedzy.json
# test prędkości dla pełnej bazy
# ENV JSON_DATABASE=large_knowledgebase.json
# COPY large_knowledgebase.json large_knowledgebase.json
RUN pip install -r requirements.txt
EXPOSE 8000
# uruchomienie środowiska produkcyjnego
CMD ["python", "main_api.py"]
# testy automatyczne fastAPI
# CMD ["pytest"]

