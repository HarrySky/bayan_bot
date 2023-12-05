FROM python:3.12-slim-bookworm as wheel-builder

RUN python -m pip install --upgrade pip && pip install --upgrade wheel
RUN pip install poetry==1.7.1

COPY . /app
WORKDIR /app
RUN poetry build -f wheel

FROM python:3.12-slim-bookworm

COPY --from=wheel-builder /app/dist/*.whl /tmp/

RUN pip install /tmp/*.whl && rm -rf /tmp/* && mkdir -p /opt/bot
WORKDIR /opt/bot
COPY migrations /opt/alembic/migrations
COPY alembic.ini /opt/alembic/alembic.ini
COPY .cd/startup /bin/startup

ENTRYPOINT ["/bin/startup"]
