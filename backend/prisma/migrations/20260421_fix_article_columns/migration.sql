-- Ensure enum exists for Article.status
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'ArticleStatus') THEN
    CREATE TYPE "ArticleStatus" AS ENUM ('draft', 'published');
  END IF;
END $$;

-- Add missing columns used by backend/controllers
ALTER TABLE "Article"
  ADD COLUMN IF NOT EXISTS "status" "ArticleStatus" NOT NULL DEFAULT 'published',
  ADD COLUMN IF NOT EXISTS "authorId" INTEGER,
  ADD COLUMN IF NOT EXISTS "coauthors" TEXT,
  ADD COLUMN IF NOT EXISTS "tagsJson" JSONB,
  ADD COLUMN IF NOT EXISTS "publishedAt" TIMESTAMP(3);

-- Helpful index for author dashboard queries
CREATE INDEX IF NOT EXISTS "Article_authorId_status_idx" ON "Article"("authorId", "status");

