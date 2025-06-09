FROM python:3.12
LABEL authors="jan"

ADD ./front/front.py .
ADD utils.py .
ADD config.json .

RUN pip install --upgrade pip
RUN pip install requests streamlit numpy pillow python-dotenv

ENTRYPOINT ["streamlit", "run"]

CMD ["front.py", "--server.port=8555"]