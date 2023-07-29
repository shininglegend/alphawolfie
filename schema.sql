-- Donations, Suggestions, sparkles cogs generate their own

-- Table: public.reactions
-- DROP TABLE IF EXISTS public.reactions;

CREATE TABLE IF NOT EXISTS reactions (
    id SERIAL PRIMARY KEY,
    trigger TEXT NOT NULL,
    eid TEXT NOT NULL,
);

-- Suggestions. This table needs a revamp!
CREATE TABLE IF NOT EXISTS public.suggestions2
(
    visual_id SERIAL NOT NULL,
    msgid bigint,
    userid bigint,
    content text UNIQUE,
    edited bigint DEFAULT 0,
    response text DEFAULT NONE,
    responseid bigint DEFAULT 0,
    id SERIAL PRIMARY KEY,
    thread bigint DEFAULT 0,
)