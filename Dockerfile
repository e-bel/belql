FROM python:3.10-slim
LABEL maintainer="Bruce Schultz"

RUN apt-get update \
    && apt-get install -y --no-install-recommends git nano \
    && pip install --upgrade pip

WORKDIR /root/app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN pip install .

EXPOSE 8080

WORKDIR /root/app/belql
ENTRYPOINT ["waitress-serve", "run:app"]