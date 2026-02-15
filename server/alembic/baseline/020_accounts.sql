-- =====================================================
-- 020_accounts.sql
-- User management for cookie-based authentication
-- =====================================================

-- ================================================
-- CORE TABLES
-- ================================================

-- Table: accounts.users
-- Description: User accounts with username/password authentication.
-- Relationships: Parent of user_feeds, user_articles, user_preferences, user_sessions
CREATE TABLE IF NOT EXISTS accounts.users (
	id UUID DEFAULT extensions.gen_random_uuid() PRIMARY KEY,
	username TEXT UNIQUE NOT NULL,
	password_hash TEXT NOT NULL,
	first_name TEXT,
	last_name TEXT,
	is_admin BOOLEAN DEFAULT FALSE NOT NULL,
	created_at TIMESTAMPTZ DEFAULT NOW(),
	updated_at TIMESTAMPTZ DEFAULT NOW(),
	last_login TIMESTAMPTZ,
	last_active TIMESTAMPTZ,
	CONSTRAINT chk_accounts_users_username_length CHECK (length(username) >= 3 AND length(username) <= 20),
	CONSTRAINT chk_accounts_users_password_hash_length CHECK (length(password_hash) >= 60),
	CONSTRAINT chk_accounts_users_first_name_length CHECK (first_name IS NULL OR length(first_name) <= 32),
	CONSTRAINT chk_accounts_users_last_name_length CHECK (last_name IS NULL OR length(last_name) <= 32)
);

DROP TRIGGER IF EXISTS trg_accounts_users_updated_at ON accounts.users;
CREATE TRIGGER trg_accounts_users_updated_at
	BEFORE UPDATE ON accounts.users
	FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

-- Table: accounts.user_sessions
-- Description: User sessions for cookie-based authentication.
-- Relationships: Child of users
CREATE TABLE IF NOT EXISTS accounts.user_sessions (
	id UUID DEFAULT extensions.gen_random_uuid() PRIMARY KEY,
	user_id UUID NOT NULL REFERENCES accounts.users(id) ON DELETE CASCADE,
	session_id UUID NOT NULL UNIQUE DEFAULT extensions.gen_random_uuid(),
	cookie_hash TEXT NOT NULL,
	expires_at TIMESTAMPTZ NOT NULL,
	created_at TIMESTAMPTZ DEFAULT NOW(),
	last_used TIMESTAMPTZ DEFAULT NOW(),
	user_agent TEXT,
	ip_address INET,
	CONSTRAINT chk_accounts_user_sessions_cookie_hash_length CHECK (length(cookie_hash) >= 64),
	CONSTRAINT chk_accounts_user_sessions_user_agent_length CHECK (user_agent IS NULL OR length(user_agent) <= 500)
);

-- ================================================
-- INDEXES
-- ================================================

-- Users indexes
CREATE INDEX IF NOT EXISTS idx_accounts_users_username ON accounts.users(username);

-- User sessions indexes
CREATE INDEX IF NOT EXISTS idx_accounts_user_sessions_user_id ON accounts.user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_accounts_user_sessions_session_id ON accounts.user_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_accounts_user_sessions_expires_at ON accounts.user_sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_accounts_user_sessions_cookie_hash ON accounts.user_sessions(cookie_hash);
CREATE INDEX IF NOT EXISTS idx_accounts_user_sessions_user_id_last_used ON accounts.user_sessions(user_id, last_used DESC);

-- ================================================
-- PERMISSIONS
-- ================================================

-- Grant table permissions to app_service (full CRUD access)
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE accounts.users TO app_service;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE accounts.user_sessions TO app_service;

-- Grant table permissions to app_readonly (read-only access)
GRANT SELECT ON TABLE accounts.users TO app_readonly;
GRANT SELECT ON TABLE accounts.user_sessions TO app_readonly;

-- Grant sequence permissions to both roles
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA accounts TO app_service, app_readonly;

-- ================================================
-- COMMENTS
-- ================================================

-- Users
COMMENT ON TABLE accounts.users IS 'User accounts with username/password authentication.';
COMMENT ON COLUMN accounts.users.username IS 'Unique username for login.';
COMMENT ON COLUMN accounts.users.password_hash IS 'PBKDF2-SHA256 hashed password.';
COMMENT ON COLUMN accounts.users.is_admin IS 'Whether user has admin privileges.';
COMMENT ON COLUMN accounts.users.last_login IS 'Timestamp of last successful login.';

-- User sessions
COMMENT ON TABLE accounts.user_sessions IS 'Active user sessions for cookie-based authentication.';
COMMENT ON COLUMN accounts.user_sessions.session_id IS 'Unique session identifier (used in token).';
COMMENT ON COLUMN accounts.user_sessions.cookie_hash IS 'SHA256 hash of session token for verification.';
COMMENT ON COLUMN accounts.user_sessions.expires_at IS 'Session expiration timestamp.';
COMMENT ON COLUMN accounts.user_sessions.last_used IS 'Last time this session was used.';
