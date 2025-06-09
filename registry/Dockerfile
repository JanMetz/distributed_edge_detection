FROM python:3.12
LABEL authors="jan"

ADD ./registry/registry.py .
ADD utils.py .
ADD resources.py .
ADD config.json .

RUN pip install --upgrade pip
RUN pip install python-dotenv fastapi requests uvicorn

CMD ["python", "./registry.py"]