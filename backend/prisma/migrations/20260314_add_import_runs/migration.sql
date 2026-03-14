ALTER TABLE "Article"
ADD COLUMN "externalUrl" TEXT,
ADD COLUMN "sourceSite" TEXT,
ADD COLUMN "sourceRssUrl" TEXT,
ADD COLUMN "guid" TEXT,
ADD COLUMN "rawHtml" TEXT,
ADD COLUMN "importedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN "updatedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP;

CREATE UNIQUE INDEX IF NOT EXISTS "Article_externalUrl_key" ON "Article"("externalUrl");
CREATE INDEX IF NOT EXISTS "Article_sourceSite_idx" ON "Article"("sourceSite");

CREATE TABLE IF NOT EXISTS "ImportRun" (
    "id" TEXT NOT NULL,
    "jobName" TEXT NOT NULL,
    "status" TEXT NOT NULL,
    "trigger" TEXT,
    "startedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "finishedAt" TIMESTAMP(3),
    "message" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "ImportRun_pkey" PRIMARY KEY ("id")
);

CREATE INDEX IF NOT EXISTS "ImportRun_jobName_status_startedAt_idx"
ON "ImportRun"("jobName", "status", "startedAt");