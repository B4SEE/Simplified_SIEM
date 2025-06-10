FROM python:3.9-slim

RUN useradd -ms /bin/bash celery

WORKDIR /www
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY start.sh /start.sh
# Fix line endings and make executable
RUN sed -i 's/\r$//' /start.sh && \
    chmod +x /start.sh && \
    chown celery:celery /start.sh

COPY . /www
RUN chown -R celery:celery /www

# Install any missing dependencies
RUN pip install --no-cache-dir flask-cors

USER celery

CMD ["/bin/bash", "/start.sh"]
