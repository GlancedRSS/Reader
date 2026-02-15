-- =====================================================
-- 010_helpers.sql
-- PostgreSQL extensions and shared utility functions
-- =====================================================

-- Enable core PostgreSQL extensions in dedicated schemas
CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA extensions;
CREATE EXTENSION IF NOT EXISTS "pgcrypto" WITH SCHEMA extensions;
CREATE EXTENSION IF NOT EXISTS "pg_trgm" WITH SCHEMA extensions;
CREATE EXTENSION IF NOT EXISTS "btree_gin" WITH SCHEMA extensions;

-- Function: public.update_updated_at_column()
-- Description: Trigger function that automatically sets updated_at to current timestamp
-- Security: Runs as table owner - safe for triggers
-- Returns: Trigger row with updated timestamp
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
	NEW.updated_at = NOW();
	RETURN NEW;
END;
$$ LANGUAGE plpgsql
SET search_path = public, extensions;

-- Function: public.generate_hash(input_text)
-- Description: Generate SHA-256 hash using pgcrypto extension
-- Security: IMMUTABLE function safe for use in indexes
-- Returns: Hexadecimal hash string
CREATE OR REPLACE FUNCTION public.generate_hash(input_text TEXT)
RETURNS TEXT AS $$
BEGIN
	RETURN encode(extensions.digest(input_text, 'sha256'), 'hex');
END;
$$ LANGUAGE plpgsql IMMUTABLE
SET search_path = public, extensions;

-- Function: public.is_valid_url(url)
-- Description: Validates URL format and checks for dangerous patterns
-- Security: IMMUTABLE function safe for constraints and indexes
-- Returns: TRUE if URL is valid for RSS feeds, FALSE otherwise
CREATE OR REPLACE FUNCTION public.is_valid_url(url TEXT)
RETURNS BOOLEAN AS $$
BEGIN
	IF url IS NULL OR length(trim(url)) = 0 THEN
		RETURN FALSE;
	END IF;

	IF length(url) < 10 OR length(url) > 2048 THEN
		RETURN FALSE;
	END IF;

	IF url !~ '^https?://.*' THEN
		RETURN FALSE;
	END IF;

	-- Complex URL validation checks:
	-- 1. Must have valid domain name (example.com) or IPv4 address, optional port
	-- 2. Must not contain invalid characters in authority section
	-- 3. Must not contain path traversal (..)
	-- 4. Must not have multiple consecutive dots (potential exploit)
	-- 5. Must not contain null bytes or shell metacharacters
	IF url !~ '://([a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(:[0-9]+)?|[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}(:[0-9]+)?)(/|\?|$)' OR
	   url ~ '://[^a-zA-Z0-9.:.-/]' OR
	   url ~ '://[^/]*\.\.' OR
	   url ~ '://[^/]*\./[^/]*\./[^/]*\.' OR
	   url ~ '\.\./' OR
	   url ~ '[\0\{\}\|\\\^`]'
	THEN
		RETURN FALSE;
	END IF;

	RETURN TRUE;
END;
$$ LANGUAGE plpgsql IMMUTABLE
SET search_path = public, extensions;

-- Function: public.sanitize_search_query(query)
-- Description: Sanitizes search queries for basic text search
-- Security: IMMUTABLE - removes @@@, |||, ; and -- characters
-- Returns: Sanitized query string safe for text search operations
CREATE OR REPLACE FUNCTION public.sanitize_search_query(query TEXT)
RETURNS TEXT AS $$
DECLARE
    sanitized_query TEXT;
    max_length INTEGER := 200;
BEGIN
	IF query IS NULL OR trim(query) = '' THEN
		RETURN '';
	END IF;

	sanitized_query := replace(query, '@@@', '');
	sanitized_query := replace(sanitized_query, '|||', '');
	sanitized_query := replace(sanitized_query, ';', '');
	sanitized_query := regexp_replace(sanitized_query, '--', '', 'g');

	IF length(sanitized_query) > max_length THEN
		sanitized_query := substring(sanitized_query FROM 1 FOR max_length);
	END IF;

	sanitized_query := regexp_replace(sanitized_query, '\s+', ' ', 'g');

	IF trim(sanitized_query) = '' THEN
		RETURN '';
	END IF;

	RETURN trim(sanitized_query);
END;
$$ LANGUAGE plpgsql IMMUTABLE
SET search_path = public, extensions;

-- Grant permissions to service role.
DO $$
BEGIN
	IF NOT EXISTS (
		SELECT 1
		FROM information_schema.role_routine_grants
		WHERE routine_schema = 'public'
		AND routine_name = 'update_updated_at_column'
		AND grantee = 'app_service'
		AND privilege_type = 'EXECUTE'
	) THEN
		GRANT EXECUTE ON FUNCTION public.update_updated_at_column() TO app_service;
	END IF;

	IF NOT EXISTS (
		SELECT 1
		FROM information_schema.role_routine_grants
		WHERE routine_schema = 'public'
		AND routine_name = 'generate_hash'
		AND grantee = 'app_service'
		AND privilege_type = 'EXECUTE'
	) THEN
		GRANT EXECUTE ON FUNCTION public.generate_hash(TEXT) TO app_service;
	END IF;

	IF NOT EXISTS (
		SELECT 1
		FROM information_schema.role_routine_grants
		WHERE routine_schema = 'public'
		AND routine_name = 'is_valid_url'
		AND grantee = 'app_service'
		AND privilege_type = 'EXECUTE'
	) THEN
		GRANT EXECUTE ON FUNCTION public.is_valid_url(TEXT) TO app_service;
	END IF;

	IF NOT EXISTS (
		SELECT 1
		FROM information_schema.role_routine_grants
		WHERE routine_schema = 'public'
		AND routine_name = 'sanitize_search_query'
		AND grantee = 'app_service'
		AND privilege_type = 'EXECUTE'
	) THEN
		GRANT EXECUTE ON FUNCTION public.sanitize_search_query(TEXT) TO app_service;
	END IF;
END $$;
