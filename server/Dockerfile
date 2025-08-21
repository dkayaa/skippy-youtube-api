FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8090

# Expose the port (optional, for documentation and inter-container communication)
EXPOSE 8090

CMD ["flask", "run"]