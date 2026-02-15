-- =====================================================
-- 050_management.sql
-- OPML import management
-- =====================================================

-- ================================================
-- OPML IMPORT TABLE
-- ================================================

-- Table: management.opml_imports
-- Description: History of OPML file imports by users
-- Relationships: Child of accounts.users with CASCADE delete
CREATE TABLE IF NOT EXISTS management.opml_imports (
	id UUID DEFAULT extensions.gen_random_uuid() PRIMARY KEY,
	user_id UUID NOT NULL REFERENCES accounts.users(id) ON DELETE CASCADE,
	filename TEXT,
	storage_key TEXT,
	status TEXT DEFAULT 'pending',
	total_feeds INTEGER DEFAULT 0,
	imported_feeds INTEGER DEFAULT 0,
	failed_feeds INTEGER DEFAULT 0,
	duplicate_feeds INTEGER DEFAULT 0,
	failed_feeds_log JSONB DEFAULT '[]',
	created_at TIMESTAMPTZ DEFAULT NOW(),
	completed_at TIMESTAMPTZ,
	CONSTRAINT chk_management_opml_imports_filename_length CHECK (filename IS NULL OR length(filename) <= 255),
	CONSTRAINT chk_management_opml_imports_storage_key_length CHECK (storage_key IS NULL OR length(storage_key) <= 500),
	CONSTRAINT chk_management_opml_imports_status CHECK (status IN ('pending', 'processing', 'completed', 'completed_with_errors', 'failed')),
	CONSTRAINT chk_management_opml_imports_feed_counts CHECK (total_feeds >= 0 AND imported_feeds >= 0 AND failed_feeds >= 0 AND duplicate_feeds >= 0),
	CONSTRAINT chk_management_opml_imports_stats CHECK (imported_feeds + failed_feeds + duplicate_feeds <= total_feeds)
);

-- ================================================
-- PERFORMANCE INDEXES
-- ================================================

-- Imports indexes
CREATE INDEX IF NOT EXISTS idx_management_opml_imports_user_status_created
ON management.opml_imports(user_id, status, created_at DESC)
WHERE status IN ('pending', 'processing', 'completed_with_errors');

CREATE INDEX IF NOT EXISTS idx_management_opml_imports_status_created_at
ON management.opml_imports(status, created_at);

-- ================================================
-- UTILITY FUNCTIONS
-- ================================================

-- Function: management.get_user_opml_history(user_id, limit, offset)
-- Description: Gets OPML import history for a user
-- Security: SECURITY DEFINER - accesses user's private data
-- Returns: Import history
CREATE OR REPLACE FUNCTION management.get_user_opml_history(
    p_user_id UUID,
    p_limit INTEGER DEFAULT 50,
    p_offset INTEGER DEFAULT 0
)
RETURNS TABLE (
    id UUID,
    type TEXT,
    filename TEXT,
    status TEXT,
    total_feeds INTEGER,
    details JSONB,
    created_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    -- Imports
    SELECT
        i.id,
        'import' as type,
        i.filename,
        i.status,
        i.total_feeds,
        jsonb_build_object(
            'imported_feeds', i.imported_feeds,
            'failed_feeds', i.failed_feeds,
            'duplicate_feeds', i.duplicate_feeds,
            'failed_feeds_log', i.failed_feeds_log
        ) as details,
        i.created_at,
        i.completed_at
    FROM management.opml_imports i
    WHERE i.user_id = p_user_id
    ORDER BY i.created_at DESC
    LIMIT p_limit OFFSET p_offset;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER
SET search_path = management, public, extensions;

-- Function: management.get_user_opml_count(user_id)
-- Description: Gets count of OPML imports for a user
-- Security: SECURITY DEFINER - aggregates user's private data
-- Returns: Count of imports
CREATE OR REPLACE FUNCTION management.get_user_opml_count(p_user_id UUID)
RETURNS BIGINT AS $$
DECLARE
    import_count BIGINT;
BEGIN
    SELECT COUNT(*) INTO import_count
    FROM management.opml_imports
    WHERE user_id = p_user_id;

    RETURN import_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER
SET search_path = management, public, extensions;

-- ================================================
-- GRANT DATA ACCESS PRIVILEGES
-- ================================================

-- Grant table and sequence permissions to application roles
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA management TO app_service;
GRANT SELECT ON ALL TABLES IN SCHEMA management TO app_readonly;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA management TO app_service, app_readonly;

-- Grant function permissions
GRANT EXECUTE ON FUNCTION management.get_user_opml_history(UUID, INTEGER, INTEGER) TO app_service, app_readonly;
GRANT EXECUTE ON FUNCTION management.get_user_opml_count(UUID) TO app_service, app_readonly;

-- ================================================
-- CROSS-SCHEMA OPERATIONS
-- ================================================

-- Add foreign key from content.user_feeds.import_id to opml_imports for rollback tracking
DO $$
BEGIN
	IF NOT EXISTS (
		SELECT 1 FROM pg_constraint
		WHERE conname = 'fk_user_feeds_import_id'
	) THEN
		ALTER TABLE content.user_feeds
		ADD CONSTRAINT fk_user_feeds_import_id
		FOREIGN KEY (import_id) REFERENCES management.opml_imports(id) ON DELETE SET NULL;
	END IF;
END $$;

-- Create index on content.user_feeds.import_id for efficient rollback queries
CREATE INDEX IF NOT EXISTS idx_content_user_feeds_import_id
ON content.user_feeds(import_id)
WHERE import_id IS NOT NULL;

-- ================================================
-- COMMENTS
-- ================================================

-- OPML Imports
COMMENT ON COLUMN management.opml_imports.filename IS 'Original filename of the uploaded OPML file.';
COMMENT ON COLUMN management.opml_imports.storage_key IS 'Local storage key for the uploaded OPML file.';
COMMENT ON COLUMN management.opml_imports.total_feeds IS 'Total number of feeds found in the OPML file.';
COMMENT ON COLUMN management.opml_imports.imported_feeds IS 'Number of feeds successfully imported.';
COMMENT ON COLUMN management.opml_imports.failed_feeds IS 'Number of feeds that failed to import.';
COMMENT ON COLUMN management.opml_imports.duplicate_feeds IS 'Number of feeds that were already subscribed.';
COMMENT ON COLUMN management.opml_imports.status IS 'Import status: pending, processing, completed, completed_with_errors, failed.';
COMMENT ON COLUMN management.opml_imports.failed_feeds_log IS 'JSON log of failed feed imports with reasons.';
COMMENT ON COLUMN management.opml_imports.completed_at IS 'Timestamp when the import completed.';

-- User Feed's Import (cross-schema reference)
COMMENT ON COLUMN content.user_feeds.import_id IS 'OPML import that created this feed subscription, for rollback support.';
