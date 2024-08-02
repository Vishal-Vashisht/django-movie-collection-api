FROM python:3.12.1-slim

WORKDIR /app

COPY requirements/ ./requirements/

RUN pip3 install --no-cache-dir -r requirements/requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]