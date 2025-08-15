FROM python:3.12-alpine3.20

COPY requirements.txt /tmp
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY ./src /src
WORKDIR /src

CMD ["opentelemetry-instrument", "--logs_exporter", "otlp", "--traces_exporter", "otlp", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5001"]
