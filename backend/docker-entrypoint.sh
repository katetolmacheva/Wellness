#!/bin/sh
set -e

echo "➡️ Running Prisma migrate..."
npx prisma migrate deploy

echo "➡️ Generating Prisma client..."
npx prisma generate

echo "➡️ Seeding database..."
npx prisma db seed

echo "➡️ Running RSS import check on startup..."
python3 -m rss_importer.main --trigger startup || true

echo "➡️ Starting RSS scheduler in background..."
python3 -m rss_importer.scheduler &

echo "➡️ Starting server..."
exec node src/server.js