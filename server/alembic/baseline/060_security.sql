-- =====================================================
-- 060_security.sql
-- Row Level Security (RLS) policies and security context
-- =====================================================

-- ================================================
-- APPLICATION CONTEXT FUNCTIONS
-- ================================================

-- Function: public.set_app_context(user_id)
-- Description: Sets user context for RLS policies from cookie session
-- Called from middleware after verifying session cookie
-- Security: SECURITY DEFINER - runs with database owner privileges
-- Returns: VOID - modifies session context
CREATE OR REPLACE FUNCTION public.set_app_context(p_user_id UUID)
RETURNS VOID AS $$
BEGIN
	PERFORM set_config('app.current_user_id', p_user_id::text, true);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER
SET search_path = public, extensions;

-- Function: public.clear_app_context()
-- Description: Clears user context (used for request cleanup)
-- Security: SECURITY DEFINER
CREATE OR REPLACE FUNCTION public.clear_app_context()
RETURNS VOID AS $$
BEGIN
	PERFORM set_config('app.current_user_id', '', true);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER
SET search_path = public, extensions;

-- Function: public.current_app_user_id()
-- Description: Retrieves current user ID from session context
-- Security: SECURITY INVOKER - runs with caller's privileges
-- Returns: UUID of current user or NULL if no context
CREATE OR REPLACE FUNCTION public.current_app_user_id()
RETURNS UUID AS $$
BEGIN
	RETURN current_setting('app.current_user_id', true)::UUID;
EXCEPTION WHEN OTHERS THEN
	RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY INVOKER
SET search_path = public, extensions;

-- ================================================
-- ROW LEVEL SECURITY POLICIES
-- ================================================

-- Contains RLS policies for personalization, content, accounts, and management tables

-- ================================================
-- PERSONALIZATION TABLE RLS POLICIES
-- ================================================

-- Enable RLS on personalization.user_preferences
DO $$
BEGIN
	IF NOT EXISTS (
		SELECT 1 FROM pg_tables
		WHERE schemaname = 'personalization'
		AND tablename = 'user_preferences'
		AND rowsecurity = true
	) THEN
		ALTER TABLE personalization.user_preferences ENABLE ROW LEVEL SECURITY;
	END IF;
END $$;

-- Policy: personalization_user_preferences_self_access_policy
-- Description: Users can only access their own preferences
DO $$
BEGIN
	IF NOT EXISTS (
		SELECT 1 FROM pg_policies
		WHERE schemaname = 'personalization'
		AND tablename = 'user_preferences'
		AND policyname = 'personalization_user_preferences_self_access_policy'
	) THEN
		CREATE POLICY personalization_user_preferences_self_access_policy ON personalization.user_preferences
			FOR ALL TO app_service, app_readonly
			USING (user_id = current_setting('app.current_user_id')::UUID)
			WITH CHECK (user_id = current_setting('app.current_user_id')::UUID);
	END IF;
END $$;

-- Enable RLS on personalization.user_folders
DO $$
BEGIN
	IF NOT EXISTS (
		SELECT 1 FROM pg_tables
		WHERE schemaname = 'personalization'
		AND tablename = 'user_folders'
		AND rowsecurity = true
	) THEN
		ALTER TABLE personalization.user_folders ENABLE ROW LEVEL SECURITY;
	END IF;
END $$;

-- Policy: personalization_user_folders_self_access_policy
-- Description: Users can only access their own folders
DO $$
BEGIN
	IF NOT EXISTS (
		SELECT 1 FROM pg_policies
		WHERE schemaname = 'personalization'
		AND tablename = 'user_folders'
		AND policyname = 'personalization_user_folders_self_access_policy'
	) THEN
		CREATE POLICY personalization_user_folders_self_access_policy ON personalization.user_folders
			FOR ALL TO app_service, app_readonly
			USING (user_id = current_setting('app.current_user_id')::UUID)
			WITH CHECK (user_id = current_setting('app.current_user_id')::UUID);
	END IF;
END $$;

-- Enable RLS on personalization.user_tags
DO $$
BEGIN
	IF NOT EXISTS (
		SELECT 1 FROM pg_tables
		WHERE schemaname = 'personalization'
		AND tablename = 'user_tags'
		AND rowsecurity = true
	) THEN
		ALTER TABLE personalization.user_tags ENABLE ROW LEVEL SECURITY;
	END IF;
END $$;

-- Policy: personalization_user_tags_self_access_policy
-- Description: Users can only access their own tags
DO $$
BEGIN
	IF NOT EXISTS (
		SELECT 1 FROM pg_policies
		WHERE schemaname = 'personalization'
		AND tablename = 'user_tags'
		AND policyname = 'personalization_user_tags_self_access_policy'
	) THEN
		CREATE POLICY personalization_user_tags_self_access_policy ON personalization.user_tags
			FOR ALL TO app_service, app_readonly
			USING (user_id = current_setting('app.current_user_id')::UUID)
			WITH CHECK (user_id = current_setting('app.current_user_id')::UUID);
	END IF;
END $$;

-- Enable RLS on personalization.tags junction table
DO $$
BEGIN
	IF NOT EXISTS (
		SELECT 1 FROM pg_tables
		WHERE schemaname = 'personalization'
		AND tablename = 'tags'
		AND rowsecurity = true
	) THEN
		ALTER TABLE personalization.tags ENABLE ROW LEVEL SECURITY;
	END IF;
END $$;

-- Policy: personalization_tags_self_access_policy
-- Description: Users can only access their own article tags
DO $$
BEGIN
	IF NOT EXISTS (
		SELECT 1 FROM pg_policies
		WHERE schemaname = 'personalization'
		AND tablename = 'tags'
		AND policyname = 'personalization_tags_self_access_policy'
	) THEN
		CREATE POLICY personalization_tags_self_access_policy ON personalization.tags
			FOR ALL TO app_service, app_readonly
			USING (
				user_tag_id IN (
					SELECT id FROM personalization.user_tags
					WHERE user_id = current_setting('app.current_user_id')::UUID
				)
			)
			WITH CHECK (
				user_tag_id IN (
					SELECT id FROM personalization.user_tags
					WHERE user_id = current_setting('app.current_user_id')::UUID
				)
			);
	END IF;
END $$;

-- ================================================
-- CONTENT TABLE RLS POLICIES
-- ================================================

-- Enable RLS on content.user_feeds
DO $$
BEGIN
	IF NOT EXISTS (
		SELECT 1 FROM pg_tables
		WHERE schemaname = 'content'
		AND tablename = 'user_feeds'
		AND rowsecurity = true
	) THEN
		ALTER TABLE content.user_feeds ENABLE ROW LEVEL SECURITY;
	END IF;
END $$;

-- Policy: content_user_feeds_self_access_policy
-- Description: Users can only access their own feed subscriptions
DO $$
BEGIN
	IF NOT EXISTS (
		SELECT 1 FROM pg_policies
		WHERE schemaname = 'content'
		AND tablename = 'user_feeds'
		AND policyname = 'content_user_feeds_self_access_policy'
	) THEN
		CREATE POLICY content_user_feeds_self_access_policy ON content.user_feeds
			FOR ALL TO app_service, app_readonly
			USING (user_id = current_setting('app.current_user_id')::UUID)
			WITH CHECK (user_id = current_setting('app.current_user_id')::UUID);
	END IF;
END $$;

-- Enable RLS on content.user_articles
DO $$
BEGIN
	IF NOT EXISTS (
		SELECT 1 FROM pg_tables
		WHERE schemaname = 'content'
		AND tablename = 'user_articles'
		AND rowsecurity = true
	) THEN
		ALTER TABLE content.user_articles ENABLE ROW LEVEL SECURITY;
	END IF;
END $$;

-- Policy: content_user_articles_self_access_policy
-- Description: Users can only access their own article states
DO $$
BEGIN
	IF NOT EXISTS (
		SELECT 1 FROM pg_policies
		WHERE schemaname = 'content'
		AND tablename = 'user_articles'
		AND policyname = 'content_user_articles_self_access_policy'
	) THEN
		CREATE POLICY content_user_articles_self_access_policy ON content.user_articles
			FOR ALL TO app_service, app_readonly
			USING (user_id = current_setting('app.current_user_id')::UUID)
			WITH CHECK (user_id = current_setting('app.current_user_id')::UUID);
	END IF;
END $$;

-- Policy: content_articles_subscription_access_policy
-- Description: Users can only access articles from their subscribed feeds
DO $$
BEGIN
	IF NOT EXISTS (
		SELECT 1 FROM pg_tables
		WHERE schemaname = 'content'
		AND tablename = 'articles'
		AND rowsecurity = true
	) THEN
		ALTER TABLE content.articles ENABLE ROW LEVEL SECURITY;
	END IF;
END $$;

DO $$
BEGIN
	IF NOT EXISTS (
		SELECT 1 FROM pg_policies
		WHERE schemaname = 'content'
		AND tablename = 'articles'
		AND policyname = 'content_articles_subscription_access_policy'
	) THEN
		CREATE POLICY content_articles_subscription_access_policy ON content.articles
			FOR ALL TO app_service, app_readonly
			USING (
				id IN (
					SELECT ASOURCE.article_id
					FROM content.article_sources ASOURCE
					JOIN content.user_feeds uf ON ASOURCE.feed_id = uf.feed_id
					WHERE uf.user_id = current_setting('app.current_user_id')::UUID
				)
			)
			WITH CHECK (
				id IN (
					SELECT ASOURCE.article_id
					FROM content.article_sources ASOURCE
					JOIN content.user_feeds uf ON ASOURCE.feed_id = uf.feed_id
					WHERE uf.user_id = current_setting('app.current_user_id')::UUID
				)
			);
	END IF;
END $$;

-- Policy: content_article_sources_subscription_access_policy
-- Description: Users can only access article sources for their subscribed feeds
DO $$
BEGIN
	IF NOT EXISTS (
		SELECT 1 FROM pg_tables
		WHERE schemaname = 'content'
		AND tablename = 'article_sources'
		AND rowsecurity = true
	) THEN
		ALTER TABLE content.article_sources ENABLE ROW LEVEL SECURITY;
	END IF;
END $$;

DO $$
BEGIN
	IF NOT EXISTS (
		SELECT 1 FROM pg_policies
		WHERE schemaname = 'content'
		AND tablename = 'article_sources'
		AND policyname = 'content_article_sources_subscription_access_policy'
	) THEN
		CREATE POLICY content_article_sources_subscription_access_policy ON content.article_sources
			FOR ALL TO app_service, app_readonly
			USING (
				feed_id IN (
					SELECT feed_id FROM content.user_feeds
					WHERE user_id = current_setting('app.current_user_id')::UUID
				)
			)
			WITH CHECK (
				feed_id IN (
					SELECT feed_id FROM content.user_feeds
					WHERE user_id = current_setting('app.current_user_id')::UUID
				)
			);
	END IF;
END $$;

-- ================================================
-- ACCOUNTS TABLE RLS POLICIES
-- ================================================

-- Enable RLS on accounts.users
DO $$
BEGIN
	IF NOT EXISTS (
		SELECT 1 FROM pg_tables
		WHERE schemaname = 'accounts'
		AND tablename = 'users'
		AND rowsecurity = true
	) THEN
		ALTER TABLE accounts.users ENABLE ROW LEVEL SECURITY;
	END IF;
END $$;

-- Policy: accounts_users_self_access_policy
-- Description: Users can only access their own account
DO $$
BEGIN
	IF NOT EXISTS (
		SELECT 1 FROM pg_policies
		WHERE schemaname = 'accounts'
		AND tablename = 'users'
		AND policyname = 'accounts_users_self_access_policy'
	) THEN
		CREATE POLICY accounts_users_self_access_policy ON accounts.users
			FOR ALL TO app_service, app_readonly
			USING (id = current_setting('app.current_user_id')::UUID)
			WITH CHECK (id = current_setting('app.current_user_id')::UUID);
	END IF;
END $$;

-- Revoke direct table access and rely on RLS policies
DO $$
BEGIN
	IF EXISTS (
		SELECT 1 FROM information_schema.role_table_grants
		WHERE table_schema = 'accounts' AND table_name = 'users'
		AND grantee = 'app_service' AND privilege_type = 'SELECT'
	) THEN
		REVOKE SELECT ON TABLE accounts.users FROM app_service;
	END IF;

	IF EXISTS (
		SELECT 1 FROM information_schema.role_table_grants
		WHERE table_schema = 'accounts' AND table_name = 'users'
		AND grantee = 'app_service' AND privilege_type = 'UPDATE'
	) THEN
		REVOKE UPDATE ON TABLE accounts.users FROM app_service;
	END IF;

	IF EXISTS (
		SELECT 1 FROM information_schema.role_table_grants
		WHERE table_schema = 'accounts' AND table_name = 'users'
		AND grantee = 'app_service' AND privilege_type = 'DELETE'
	) THEN
		REVOKE DELETE ON TABLE accounts.users FROM app_service;
	END IF;

	IF EXISTS (
		SELECT 1 FROM information_schema.role_table_grants
		WHERE table_schema = 'accounts' AND table_name = 'users'
		AND grantee = 'app_readonly' AND privilege_type = 'SELECT'
	) THEN
		REVOKE SELECT ON TABLE accounts.users FROM app_readonly;
	END IF;
END $$;

-- Grant minimal SELECT access for RLS policies to work
DO $$
BEGIN
	IF NOT EXISTS (
		SELECT 1 FROM information_schema.role_table_grants
		WHERE table_schema = 'accounts' AND table_name = 'users'
		AND grantee = 'app_service' AND privilege_type = 'SELECT'
	) THEN
		GRANT SELECT ON TABLE accounts.users TO app_service;
	END IF;

	IF NOT EXISTS (
		SELECT 1 FROM information_schema.role_table_grants
		WHERE table_schema = 'accounts' AND table_name = 'users'
		AND grantee = 'app_readonly' AND privilege_type = 'SELECT'
	) THEN
		GRANT SELECT ON TABLE accounts.users TO app_readonly;
	END IF;
END $$;

-- ================================================
-- MANAGEMENT TABLE RLS POLICIES
-- ================================================

-- Enable RLS on management.opml_imports
DO $$
BEGIN
	IF NOT EXISTS (
		SELECT 1 FROM pg_tables
		WHERE schemaname = 'management'
		AND tablename = 'opml_imports'
		AND rowsecurity = true
	) THEN
		ALTER TABLE management.opml_imports ENABLE ROW LEVEL SECURITY;
	END IF;
END $$;

-- Policy: management_opml_imports_self_access_policy
-- Description: Users can only access their own OPML imports
DO $$
BEGIN
	IF NOT EXISTS (
		SELECT 1 FROM pg_policies
		WHERE schemaname = 'management'
		AND tablename = 'opml_imports'
		AND policyname = 'management_opml_imports_self_access_policy'
	) THEN
		CREATE POLICY management_opml_imports_self_access_policy ON management.opml_imports
			FOR ALL TO app_service, app_readonly
			USING (user_id = current_setting('app.current_user_id')::UUID)
			WITH CHECK (user_id = current_setting('app.current_user_id')::UUID);
	END IF;
END $$;

-- ================================================
-- GRANT SECURITY FUNCTION PRIVILEGES
-- ================================================

-- Grant execute permissions on security context functions
GRANT EXECUTE ON FUNCTION public.set_app_context TO app_service;
GRANT EXECUTE ON FUNCTION public.clear_app_context TO app_service;
GRANT EXECUTE ON FUNCTION public.current_app_user_id TO app_service, app_readonly;
