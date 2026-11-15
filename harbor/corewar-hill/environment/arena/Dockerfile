FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends gcc make libc6-dev \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir mcp==1.30.0
COPY pmars /srv/pmars
RUN make -C /srv/pmars pmars
COPY arena /srv/arena
COPY data /srv/data
RUN chmod -R a+rX /srv
ENV PYTHONPATH=/srv
RUN mkdir -p /results/history && touch /results/submission.red /results/events.jsonl
EXPOSE 8000
CMD ["python", "-m", "arena.mcp_server"]
