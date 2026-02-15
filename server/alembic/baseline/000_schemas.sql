-- =====================================================
-- 000_schemas.sql
-- Database roles, schemas, and security configuration
-- =====================================================

-- ================================================
-- ROLE HIERARCHY
-- ================================================

-- app_owner: Database owner with full privileges
-- app_service: Application service role for read/write operations
-- app_readonly: Read-only role for reporting and analytics

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_owner') THEN
    CREATE ROLE app_owner NOINHERIT;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_service') THEN
    CREATE ROLE app_service NOINHERIT;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_readonly') THEN
    CREATE ROLE app_readonly NOINHERIT;
  END IF;
END $$;

-- ================================================
-- SCHEMA CREATION
-- ================================================

CREATE SCHEMA IF NOT EXISTS extensions;
CREATE SCHEMA IF NOT EXISTS accounts;
CREATE SCHEMA IF NOT EXISTS content;
CREATE SCHEMA IF NOT EXISTS personalization;
CREATE SCHEMA IF NOT EXISTS management;

DO $$
BEGIN
  IF (SELECT nspowner FROM pg_namespace WHERE nspname = 'extensions') !=
     (SELECT oid FROM pg_roles WHERE rolname = 'app_owner') THEN
    ALTER SCHEMA extensions OWNER TO app_owner;
  END IF;

  IF (SELECT nspowner FROM pg_namespace WHERE nspname = 'accounts') !=
     (SELECT oid FROM pg_roles WHERE rolname = 'app_owner') THEN
    ALTER SCHEMA accounts OWNER TO app_owner;
  END IF;

  IF (SELECT nspowner FROM pg_namespace WHERE nspname = 'content') !=
     (SELECT oid FROM pg_roles WHERE rolname = 'app_owner') THEN
    ALTER SCHEMA content OWNER TO app_owner;
  END IF;

  IF (SELECT nspowner FROM pg_namespace WHERE nspname = 'personalization') !=
     (SELECT oid FROM pg_roles WHERE rolname = 'app_owner') THEN
    ALTER SCHEMA personalization OWNER TO app_owner;
  END IF;

  IF (SELECT nspowner FROM pg_namespace WHERE nspname = 'management') !=
     (SELECT oid FROM pg_roles WHERE rolname = 'app_owner') THEN
    ALTER SCHEMA management OWNER TO app_owner;
  END IF;
END $$;

-- ================================================
-- SCHEMA OWNERSHIP
-- ================================================

GRANT USAGE ON SCHEMA extensions TO app_service;
GRANT USAGE ON SCHEMA accounts TO app_service;
GRANT USAGE ON SCHEMA content TO app_service;
GRANT USAGE ON SCHEMA personalization TO app_service;
GRANT USAGE ON SCHEMA management TO app_service;

GRANT USAGE ON SCHEMA extensions TO app_readonly;
GRANT USAGE ON SCHEMA accounts TO app_readonly;
GRANT USAGE ON SCHEMA content TO app_readonly;
GRANT USAGE ON SCHEMA personalization TO app_readonly;
GRANT USAGE ON SCHEMA management TO app_readonly;

-- ================================================
-- DEFAULT PRIVILEGES
-- ================================================

ALTER DEFAULT PRIVILEGES IN SCHEMA accounts
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_service;
ALTER DEFAULT PRIVILEGES IN SCHEMA content
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_service;
ALTER DEFAULT PRIVILEGES IN SCHEMA personalization
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_service;
ALTER DEFAULT PRIVILEGES IN SCHEMA management
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_service;

ALTER DEFAULT PRIVILEGES IN SCHEMA accounts
  GRANT SELECT ON TABLES TO app_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA content
  GRANT SELECT ON TABLES TO app_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA personalization
  GRANT SELECT ON TABLES TO app_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA management
  GRANT SELECT ON TABLES TO app_readonly;

ALTER DEFAULT PRIVILEGES IN SCHEMA accounts
  GRANT USAGE, SELECT ON SEQUENCES TO app_service;
ALTER DEFAULT PRIVILEGES IN SCHEMA content
  GRANT USAGE, SELECT ON SEQUENCES TO app_service;
ALTER DEFAULT PRIVILEGES IN SCHEMA personalization
  GRANT USAGE, SELECT ON SEQUENCES TO app_service;
ALTER DEFAULT PRIVILEGES IN SCHEMA management
  GRANT USAGE, SELECT ON SEQUENCES TO app_service;

ALTER DEFAULT PRIVILEGES IN SCHEMA extensions
  GRANT EXECUTE ON FUNCTIONS TO app_service;
ALTER DEFAULT PRIVILEGES IN SCHEMA extensions
  GRANT EXECUTE ON FUNCTIONS TO app_readonly;

-- ================================================
-- DATABASE CONFIGURATION
-- ================================================

DO $$
DECLARE
  db_name text := current_database();
  current_search_path text;
BEGIN
  BEGIN
    SELECT current_setting('search_path', true) INTO current_search_path;
  EXCEPTION WHEN OTHERS THEN
    current_search_path := '';
  END;

  IF current_search_path IS DISTINCT FROM 'public, accounts, content, personalization, management, extensions' THEN
    EXECUTE format(
      'ALTER DATABASE %I SET search_path TO public, accounts, content, personalization, management, extensions',
      db_name
    );
  END IF;
END $$;

DO $$
DECLARE
  current_row_security text;
BEGIN
  BEGIN
    SELECT current_setting('row_security', true) INTO current_row_security;
  EXCEPTION WHEN OTHERS THEN
    current_row_security := '';
  END;

  IF current_row_security IS DISTINCT FROM 'on' THEN
    EXECUTE format('ALTER DATABASE %I SET row_security = ON', current_database());
  END IF;
END $$;

-- ================================================
-- SCHEMA COMMENTS
-- ================================================

DO $$
BEGIN
  IF pg_catalog.obj_description('accounts'::regnamespace, 'pg_namespace') IS DISTINCT FROM
     'Identity profiles and user authentication' THEN
    COMMENT ON SCHEMA accounts IS 'Identity profiles and user authentication';
  END IF;

  IF pg_catalog.obj_description('content'::regnamespace, 'pg_namespace') IS DISTINCT FROM
     'Feeds, articles, and user content interactions' THEN
    COMMENT ON SCHEMA content IS 'Feeds, articles, and user content interactions';
  END IF;

  IF pg_catalog.obj_description('personalization'::regnamespace, 'pg_namespace') IS DISTINCT FROM
     'User preferences, personal organization, and activity tracking' THEN
    COMMENT ON SCHEMA personalization IS 'User preferences, personal organization, and activity tracking';
  END IF;

  IF pg_catalog.obj_description('management'::regnamespace, 'pg_namespace') IS DISTINCT FROM
     'Data import/export utilities and system management' THEN
    COMMENT ON SCHEMA management IS 'Data import/export utilities and system management';
  END IF;
END $$;
