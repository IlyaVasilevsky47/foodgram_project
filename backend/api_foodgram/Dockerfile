FROM python:3.8-slim

WORKDIR /app

COPY . .

COPY requirements.txt .

RUN pip3 install -r requirements.txt --no-cache-dir

COPY static/data/ ./static/data/

CMD ["gunicorn", "api_foodgram.wsgi:application", "--bind", "0:8000"]