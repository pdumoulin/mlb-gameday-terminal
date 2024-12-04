FROM python:3.13.0-slim-bookworm AS base

WORKDIR /var/app

RUN apt update && \
    apt install -y watch locales && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen && locale-gen en_US.UTF-8
ENV LC_ALL=en_US.UTF-8

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY run.sh run.py games.p teams.py ./

RUN useradd -ms /bin/bash appuser
USER appuser
ENTRYPOINT ["./run.sh"]
