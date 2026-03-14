FROM node:20-bookworm-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    openssl \
    ca-certificates \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Node dependencies
COPY package.json package-lock.json* ./
RUN npm ci || npm install

# Python dependencies for RSS importer
COPY rss_importer/requirements.txt ./rss_importer/requirements.txt
RUN python3 -m venv /opt/venv
RUN /opt/venv/bin/pip install --no-cache-dir -r ./rss_importer/requirements.txt

# Copy project
COPY . .

# Prisma
RUN npx prisma generate

# Static images dir
RUN mkdir -p /app/public/images/articles
RUN chmod +x /app/docker-entrypoint.sh

ENV PATH="/opt/venv/bin:$PATH"

EXPOSE 3001

CMD ["sh", "./docker-entrypoint.sh"]