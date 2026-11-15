FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends gcc make libc6-dev \
    && rm -rf /var/lib/apt/lists/*
COPY . /tests/
RUN make -C /tests/pmars pmars && chmod -R a+rX /tests
WORKDIR /tests
