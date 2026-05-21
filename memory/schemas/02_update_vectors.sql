-- Update embedding dimension to match our local model (384 dims)
-- all-MiniLM-L6-v2 uses 384, not OpenAI's 1536

ALTER TABLE memories DROP COLUMN IF EXISTS embedding;
ALTER TABLE memories ADD COLUMN embedding vector(384);

-- Recreate index with correct dimensions
DROP INDEX IF EXISTS memories_embedding_idx;
CREATE INDEX memories_embedding_idx
    ON memories USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 10);