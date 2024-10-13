FROM python:3.12-slim as python-base
ENV PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    \
    # pip
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

RUN addgroup --gid 1000 webapp
RUN adduser -u 1000 --gid 1000 webapp
USER webapp

COPY --chown=webapp:webapp . /app/
WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000
CMD ["python", "-m", "bin.start_api"]
#ENTRYPOINT ["./entry.sh"]
#CMD ["web-local"]
