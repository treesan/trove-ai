-- Add embedding column for semantic search
-- 1024-dim: bge-m3 (multilingual). Dimension is normalized/idempotently migrated by 008.
ALTER TABLE articles ADD COLUMN IF NOT EXISTS embedding vector(1024);

-- Index for cosine similarity search (ivfflat for performance)
CREATE INDEX IF NOT EXISTS idx_articles_embedding ON articles
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
