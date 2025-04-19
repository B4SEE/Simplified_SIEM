FROM python:3.9-slim

WORKDIR /www

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . /www

CMD ["python", "run.py"]