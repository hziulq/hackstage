# dev / prod はローカルと Render で同じ Dockerfile を使う(docs/design.md §12)
FROM python:3.12-slim AS base
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── ローカル開発(compose) ──────────────────────────
FROM base AS dev
ENV FLASK_APP=wsgi.py \
    FLASK_RUN_HOST=0.0.0.0 \
    FLASK_RUN_PORT=8000
COPY . .
CMD ["flask", "run", "--debug"]

# ── 本番(Render, dockerTarget: prod) ────────────────
FROM base AS prod
COPY . .
ENV PORT=8000
CMD ["sh", "-c", "gunicorn -w 4 -b 0.0.0.0:${PORT} wsgi:app"]
