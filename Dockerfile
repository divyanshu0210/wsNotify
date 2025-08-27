FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential libpq-dev \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# collectstatic if using Django static files
# RUN python manage.py collectstatic --noinput

CMD ["daphne", "-b", "0.0.0.0", "-p", "8080", "wsnotify.asgi:application"]
