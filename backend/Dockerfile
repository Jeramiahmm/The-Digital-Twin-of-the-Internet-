FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend/ ./backend/
COPY simulation/ ./simulation/

EXPOSE 8000

CMD ["python", "-m", "backend.main"]
