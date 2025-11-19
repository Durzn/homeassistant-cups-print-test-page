FROM python:3.12-alpine

RUN apk add --no-cache bash cups-dev cups-libs cups-client libc-dev gcc python3-dev
RUN pip install flask pycups reportlab gunicorn

WORKDIR /app
COPY cups_server.py run.sh /app/
RUN chmod +x /app/run.sh
CMD ["/app/run.sh"]