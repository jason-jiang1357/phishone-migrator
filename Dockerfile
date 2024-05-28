FROM python:3.12.3-slim

RUN pip install aiohttp

WORKDIR /phishone_migrator

COPY ./src/ /phishone_migrator/
