FROM python:3.12
LABEL authors="jan"

ADD ./back/backend.py .
ADD utils.py .
ADD resources.py .
ADD config.json .

RUN pip install --upgrade pip
RUN pip install requests python-dotenv fastapi uvicorn python-multipart

CMD ["python", "./backend.py"]