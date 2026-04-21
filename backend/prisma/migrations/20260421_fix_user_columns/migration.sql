-- Add missing columns to User table to match Prisma schema
ALTER TABLE "User"
  ADD COLUMN IF NOT EXISTS "avatarUrl" TEXT,
  ADD COLUMN IF NOT EXISTS "expert_document_url" TEXT,
  ADD COLUMN IF NOT EXISTS "expert_document_name" TEXT,
  ADD COLUMN IF NOT EXISTS "expert_verification_note" TEXT;

