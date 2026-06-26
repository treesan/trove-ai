-- Normalize the semantic-search embedding column to vector(1024) for bge-m3.
--
-- History: the column was vector(384) -> vector(512) (bge-small-zh) -> now vector(1024) (bge-m3).
-- This migration is idempotent: it only fires when the column is NOT already vector(1024).
-- When it fires it clears all existing vectors (they are the wrong dimension and/or from a
-- different model); the auto-backfill task then regenerates them with the configured model.
DO $$
DECLARE
    cur_type text;
BEGIN
    SELECT format_type(atttypid, atttypmod) INTO cur_type
    FROM pg_attribute
    WHERE attrelid = 'articles'::regclass
      AND attname = 'embedding'
      AND NOT attisdropped;

    IF cur_type IS DISTINCT FROM 'vector(1024)' THEN
        DROP INDEX IF EXISTS idx_articles_embedding;
        ALTER TABLE articles ALTER COLUMN embedding TYPE vector(1024) USING NULL;
        CREATE INDEX idx_articles_embedding ON articles
            USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
        RAISE NOTICE 'embedding column migrated to vector(1024); old vectors cleared for re-backfill';
    END IF;
END $$;
