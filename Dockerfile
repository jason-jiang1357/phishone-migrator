FROM python:3.12.3-slim

RUN pip install aiohttp

WORKDIR /phishone_migrator

COPY ./src/ /phishone_migrator/

# 备份的数据包
COPY ./backup_data /backup_data