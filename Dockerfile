FROM python:3.12-alpine
LABEL maintainer="i.antonishak@gmail.com"

WORKDIR /olx_scraper

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .
