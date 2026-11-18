FROM python:3.9-slim

# Устанавливаем зависимости для работы с PostgreSQL
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Устанавливаем библиотеку psycopg2 для Python
RUN pip install psycopg2-binary

COPY app.py .

EXPOSE 8080

CMD ["python", "app.py"]