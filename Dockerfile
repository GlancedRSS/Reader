FROM node:24-alpine AS frontend-builder
WORKDIR /app

ENV NEXT_PUBLIC_API_URL=http://backend:2076

COPY app/package.json ./
RUN npm install

COPY app/ .
RUN npm run build

FROM python:3.13-alpine AS backend-builder

RUN apk add --no-cache gcc musl-dev postgresql-dev

COPY server /tmp/server
RUN python -m venv /venv && \
    /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install /tmp/server && \
    rm -rf /tmp/server

FROM python:3.13-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV PORT=2077
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

COPY --from=frontend-builder /usr/local/bin/node /usr/local/bin/

RUN apk add --no-cache libstdc++ libgcc postgresql-libs postgresql-client wget

RUN adduser -D -u 1000 appuser

COPY --from=frontend-builder /app/public /app/public
COPY --from=frontend-builder --chown=appuser:appuser /app/.next/standalone /app/
COPY --from=frontend-builder --chown=appuser:appuser /app/.next/static /app/.next/static

COPY --from=backend-builder --chown=appuser:appuser /venv /venv

COPY --chown=appuser:appuser server/alembic /server/alembic
COPY --chown=appuser:appuser server/alembic.ini /server/alembic.ini

COPY --chmod=755 docker-entrypoint.sh /docker-entrypoint.sh

RUN mkdir -p /data /logs && chown appuser:appuser /data /logs

USER appuser
ENV PATH=/venv/bin:$PATH
EXPOSE 2076 2077

ENTRYPOINT ["/docker-entrypoint.sh"]
