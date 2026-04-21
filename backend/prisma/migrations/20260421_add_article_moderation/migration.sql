-- AlterTable
ALTER TABLE "Article"
ADD COLUMN "moderationStatus" TEXT NOT NULL DEFAULT 'pending',
ADD COLUMN "moderationReason" TEXT,
ADD COLUMN "moderationScore" INTEGER,
ADD COLUMN "moderatedAt" TIMESTAMP(3);
