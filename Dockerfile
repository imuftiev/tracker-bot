FROM python:3.11-alpine
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
CMD alembic upgrade head && python bot.py
