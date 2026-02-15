-- =====================================================
-- 030_content.sql
-- Unified content schema: feeds, articles, and content management
-- =====================================================

-- ================================================
-- CORE TABLES
-- ================================================

-- Table: content.feeds
-- Description: Unified feed definitions for RSS/Atom feeds
-- Relationships: Has many user_feeds, has many articles through article_sources
CREATE TABLE IF NOT EXISTS content.feeds (
	id UUID DEFAULT extensions.gen_random_uuid() PRIMARY KEY,
	title TEXT NOT NULL,
	description TEXT,
	feed_type TEXT NOT NULL DEFAULT 'rss',
	language TEXT,
	website TEXT,
	canonical_url TEXT,
	latest_articles UUID[] DEFAULT '{}',
	last_update TIMESTAMPTZ,
	last_fetched_at TIMESTAMPTZ,
	is_active BOOLEAN DEFAULT true,
	error_count INTEGER DEFAULT 0,
	last_error TEXT,
	last_error_at TIMESTAMPTZ,
	created_at TIMESTAMPTZ DEFAULT NOW(),
	updated_at TIMESTAMPTZ DEFAULT NOW(),
	CONSTRAINT chk_content_feeds_title_length CHECK (length(title) <= 500),
	CONSTRAINT chk_content_feeds_description_length CHECK (description IS NULL OR length(description) <= 2000),
	CONSTRAINT chk_content_feeds_feed_type CHECK (feed_type IN ('rss', 'atom')),
	CONSTRAINT chk_content_feeds_language CHECK (language IS NULL OR language ~ '^[a-z]{2}(-[A-Z]{2})?$'),
	CONSTRAINT chk_content_feeds_website CHECK (website IS NULL OR public.is_valid_url(website)),
	CONSTRAINT chk_content_feeds_canonical_url CHECK (canonical_url IS NULL OR public.is_valid_url(canonical_url)),
	CONSTRAINT chk_content_feeds_error_count CHECK (error_count >= 0),
	CONSTRAINT chk_content_feeds_last_error_length CHECK (last_error IS NULL OR length(last_error) <= 2000)
);

-- Table: content.articles
-- Description: Unified articles from feeds, deduplicated by canonical URL
-- Relationships: Has many article_sources, has many user_articles
CREATE TABLE IF NOT EXISTS content.articles (
	id UUID DEFAULT extensions.gen_random_uuid() PRIMARY KEY,
	canonical_url TEXT UNIQUE,
	title TEXT,
	author TEXT,
	summary TEXT,
	content TEXT,
	textsearchable tsvector NOT NULL,
	source_tags TEXT[] DEFAULT '{}',
	media_url TEXT,
	platform_metadata JSONB DEFAULT '{}',
	published_at TIMESTAMPTZ,
	created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
	CONSTRAINT chk_content_articles_canonical_url CHECK (public.is_valid_url(canonical_url)),
	CONSTRAINT chk_content_articles_title_length CHECK (title IS NULL OR length(title) <= 1000),
	CONSTRAINT chk_content_articles_author_length CHECK (author IS NULL OR length(author) <= 500),
	CONSTRAINT chk_content_articles_summary_length CHECK (summary IS NULL OR length(summary) <= 2000),
	CONSTRAINT chk_content_articles_media_url CHECK (media_url IS NULL OR public.is_valid_url(media_url)),
	CONSTRAINT chk_content_articles_published_not_future CHECK (published_at IS NULL OR published_at <= NOW())
);


-- ================================================
-- USER-SPECIFIC TABLES
-- ================================================

-- Table: content.user_feeds
-- Description: User subscriptions to feeds
-- Relationships: Belongs to user and feed, belongs to folder, belongs to opml_imports
-- Note: Foreign keys to personalization and management schemas added in later migrations
CREATE TABLE IF NOT EXISTS content.user_feeds (
	id UUID DEFAULT extensions.gen_random_uuid() PRIMARY KEY,
	user_id UUID NOT NULL REFERENCES accounts.users(id) ON DELETE CASCADE,
	feed_id UUID NOT NULL REFERENCES content.feeds(id) ON DELETE CASCADE,
	title TEXT NOT NULL,
	is_pinned BOOLEAN DEFAULT false,
	is_active BOOLEAN DEFAULT true,
	unread_count INTEGER DEFAULT 0,
	created_at TIMESTAMPTZ DEFAULT NOW(),
	folder_id UUID,
	import_id UUID,
	UNIQUE(user_id, feed_id),
	CONSTRAINT chk_content_user_feeds_title_length CHECK (length(title) <= 200),
	CONSTRAINT chk_content_user_feeds_unread_count CHECK (unread_count >= 0)
);


-- Table: content.user_articles
-- Description: User-specific article states (read/unread, read later)
-- Relationships: Belongs to user and article
CREATE TABLE IF NOT EXISTS content.user_articles (
	id UUID DEFAULT extensions.gen_random_uuid() PRIMARY KEY,
	user_id UUID NOT NULL REFERENCES accounts.users(id) ON DELETE CASCADE,
	article_id UUID NOT NULL REFERENCES content.articles(id) ON DELETE CASCADE,
	is_read BOOLEAN DEFAULT false,
	read_at TIMESTAMPTZ,
	read_later BOOLEAN DEFAULT false,
	created_at TIMESTAMPTZ DEFAULT NOW(),
	UNIQUE(user_id, article_id)
);


-- ================================================
-- JUNCTION TABLES
-- ================================================

-- Table: content.article_sources
-- Description: Junction table linking articles to their source feeds
-- Relationships: Junction between articles and feeds
CREATE TABLE IF NOT EXISTS content.article_sources (
	id UUID DEFAULT extensions.gen_random_uuid() PRIMARY KEY,
	article_id UUID NOT NULL REFERENCES content.articles(id) ON DELETE CASCADE,
	feed_id UUID NOT NULL REFERENCES content.feeds(id) ON DELETE CASCADE,
	UNIQUE(article_id, feed_id)
);


-- ================================================
-- INDEXES
-- ================================================

-- feeds indexes
CREATE UNIQUE INDEX IF NOT EXISTS idx_content_feeds_canonical_url_unique ON content.feeds(canonical_url) WHERE canonical_url IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_content_feeds_last_fetched_at ON content.feeds(last_fetched_at);
CREATE INDEX IF NOT EXISTS idx_content_feeds_last_update_desc ON content.feeds(last_update DESC NULLS LAST);
CREATE INDEX IF NOT EXISTS idx_content_feeds_latest_articles ON content.feeds USING GIN(latest_articles);
CREATE INDEX IF NOT EXISTS idx_content_feeds_error_count ON content.feeds(error_count) WHERE error_count > 0;
CREATE INDEX IF NOT EXISTS idx_content_feeds_active_type ON content.feeds(is_active, feed_type) WHERE is_active = true;

-- articles indexes
CREATE INDEX IF NOT EXISTS idx_content_articles_canonical_url ON content.articles(canonical_url);
CREATE INDEX IF NOT EXISTS idx_content_articles_published_id_cursor ON content.articles(published_at DESC, id DESC);

-- articles search indexes (trigram for fuzzy matching)
SET search_path TO content, public, extensions;
CREATE INDEX IF NOT EXISTS idx_content_articles_title_trgm ON content.articles USING GIN(title gin_trgm_ops);
RESET search_path;

-- articles full-text search index
CREATE INDEX IF NOT EXISTS idx_content_articles_textsearchable ON content.articles USING GIN(textsearchable);

-- articles platform_metadata index for platform-specific queries
CREATE INDEX IF NOT EXISTS idx_content_articles_platform_metadata_gin ON content.articles USING GIN(platform_metadata);

-- composite indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_content_user_articles_user_read ON content.user_articles(user_id, is_read) WHERE is_read = false;
CREATE INDEX IF NOT EXISTS idx_content_user_articles_user_read_later ON content.user_articles(user_id, read_later) WHERE read_later = true;
CREATE INDEX IF NOT EXISTS idx_content_user_feeds_user_folder ON content.user_feeds(user_id, folder_id) WHERE folder_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_content_article_sources_article_feed ON content.article_sources(article_id, feed_id);

-- user_feeds indexes
CREATE INDEX IF NOT EXISTS idx_content_user_feeds_feed_id ON content.user_feeds(feed_id);
CREATE INDEX IF NOT EXISTS idx_content_user_feeds_folder_id ON content.user_feeds(folder_id) WHERE folder_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_content_user_feeds_pinned_sort ON content.user_feeds(user_id, is_pinned DESC, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_content_user_feeds_active ON content.user_feeds(user_id, is_active) WHERE is_active = true;

-- user_articles indexes
CREATE INDEX IF NOT EXISTS idx_content_user_articles_article_id ON content.user_articles(article_id);
CREATE INDEX IF NOT EXISTS idx_content_user_articles_read_later ON content.user_articles(user_id, read_later) WHERE read_later = true;

-- article_sources indexes
CREATE INDEX IF NOT EXISTS idx_content_article_sources_article_id ON content.article_sources(article_id);
CREATE INDEX IF NOT EXISTS idx_content_article_sources_feed_id ON content.article_sources(feed_id);

-- ================================================
-- TRIGGERS
-- ================================================

-- Trigger for feeds.updated_at
DROP TRIGGER IF EXISTS trg_content_feeds_updated_at ON content.feeds;
CREATE TRIGGER trg_content_feeds_updated_at
	BEFORE UPDATE ON content.feeds
	FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

-- Function: content.update_user_feed_unread_count_on_read_change()
-- Description: Updates unread count when an article's read state changes
-- Security: SECURITY DEFINER - handles complex multi-table logic
CREATE OR REPLACE FUNCTION content.update_user_feed_unread_count_on_read_change()
RETURNS TRIGGER AS $$
DECLARE
	feed_ids UUID[];
	v_feed_id UUID;
BEGIN
    IF TG_OP = 'INSERT' THEN
        IF NEW.is_read = false THEN
            -- Find all feeds this article appears in that the user subscribes to
            feed_ids := ARRAY(
                SELECT DISTINCT uf.feed_id
                FROM content.user_feeds uf
                WHERE uf.user_id = NEW.user_id
                AND EXISTS (
                    SELECT 1 FROM content.article_sources ASOURCE
                    WHERE ASOURCE.feed_id = uf.feed_id
                    AND ASOURCE.article_id = NEW.article_id
                )
            );

            -- Increment unread count for each feed
            FOREACH v_feed_id IN ARRAY feed_ids
            LOOP
                UPDATE content.user_feeds
                SET unread_count = unread_count + 1
                WHERE feed_id = v_feed_id AND user_id = NEW.user_id;
            END LOOP;
        END IF;
        RETURN NEW;

    ELSIF TG_OP = 'UPDATE' THEN
        IF OLD.is_read = false AND NEW.is_read = true THEN
            -- Article marked as read - decrement counts
            feed_ids := ARRAY(
                SELECT DISTINCT uf.feed_id
                FROM content.user_feeds uf
                WHERE uf.user_id = NEW.user_id
                AND EXISTS (
                    SELECT 1 FROM content.article_sources ASOURCE
                    WHERE ASOURCE.feed_id = uf.feed_id
                    AND ASOURCE.article_id = NEW.article_id
                )
            );

            FOREACH v_feed_id IN ARRAY feed_ids
            LOOP
                UPDATE content.user_feeds
                SET unread_count = GREATEST(unread_count - 1, 0)
                WHERE feed_id = v_feed_id AND user_id = NEW.user_id;
            END LOOP;

        ELSIF OLD.is_read = true AND NEW.is_read = false THEN
            -- Article marked as unread - increment counts
            feed_ids := ARRAY(
                SELECT DISTINCT uf.feed_id
                FROM content.user_feeds uf
                WHERE uf.user_id = NEW.user_id
                AND EXISTS (
                    SELECT 1 FROM content.article_sources ASOURCE
                    WHERE ASOURCE.feed_id = uf.feed_id
                    AND ASOURCE.article_id = NEW.article_id
                )
            );

            FOREACH v_feed_id IN ARRAY feed_ids
            LOOP
                UPDATE content.user_feeds
                SET unread_count = unread_count + 1
                WHERE feed_id = v_feed_id AND user_id = NEW.user_id;
            END LOOP;
        END IF;
        RETURN NEW;

    ELSIF TG_OP = 'DELETE' THEN
        IF OLD.is_read = false THEN
            -- Unread article deleted - decrement counts
            feed_ids := ARRAY(
                SELECT DISTINCT uf.feed_id
                FROM content.user_feeds uf
                WHERE uf.user_id = OLD.user_id
                AND EXISTS (
                    SELECT 1 FROM content.article_sources ASOURCE
                    WHERE ASOURCE.feed_id = uf.feed_id
                    AND ASOURCE.article_id = OLD.article_id
                )
            );

            FOREACH v_feed_id IN ARRAY feed_ids
            LOOP
                UPDATE content.user_feeds
                SET unread_count = GREATEST(unread_count - 1, 0)
                WHERE feed_id = v_feed_id AND user_id = OLD.user_id;
            END LOOP;
        END IF;
        RETURN OLD;
    END IF;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER
SET search_path = content, public, extensions;

-- Trigger to maintain unread counts when article states change
DROP TRIGGER IF EXISTS trg_content_user_articles_update_unread_counts ON content.user_articles;
CREATE TRIGGER trg_content_user_articles_update_unread_counts
    AFTER INSERT OR UPDATE OR DELETE ON content.user_articles
    FOR EACH ROW
    EXECUTE FUNCTION content.update_user_feed_unread_count_on_read_change();

-- Function: content.recalculate_user_feed_unread_count(user_feed_id)
-- Description: Recalculates unread count for a specific user feed subscription (data fixes)
-- Security: SECURITY DEFINER - performs complex aggregation queries
CREATE OR REPLACE FUNCTION content.recalculate_user_feed_unread_count(p_user_feed_id UUID)
RETURNS INTEGER AS $$
DECLARE
    new_count INTEGER;
    v_user_id UUID;
    v_feed_id UUID;
BEGIN
    SELECT user_id, feed_id INTO v_user_id, v_feed_id
    FROM content.user_feeds
    WHERE id = p_user_feed_id;

    SELECT COUNT(DISTINCT a.id) INTO new_count
    FROM content.articles a
    JOIN content.user_articles ua ON (
        a.id = ua.article_id
        AND ua.user_id = v_user_id
    )
    WHERE ua.is_read = FALSE
    AND EXISTS (
        SELECT 1 FROM content.article_sources ASOURCE
        WHERE ASOURCE.feed_id = v_feed_id
        AND ASOURCE.article_id = a.id
    );

    UPDATE content.user_feeds
    SET unread_count = new_count
    WHERE id = p_user_feed_id;

    RETURN new_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER
SET search_path = content, public, extensions;

-- Function: content.recalculate_all_user_feed_unread_counts(user_uuid)
-- Description: Recalculates all feed unread counts for a user (data fixes)
-- Security: SECURITY DEFINER - performs bulk updates across subscriptions
CREATE OR REPLACE FUNCTION content.recalculate_all_user_feed_unread_counts(p_user_uuid UUID)
RETURNS VOID AS $$
BEGIN
    UPDATE content.user_feeds uf
    SET unread_count = (
        SELECT COUNT(DISTINCT a.id)
        FROM content.articles a
        JOIN content.user_articles ua ON (
            a.id = ua.article_id AND ua.user_id = p_user_uuid
        )
        WHERE ua.is_read = FALSE
        AND EXISTS (
            SELECT 1 FROM content.article_sources ASOURCE
            WHERE ASOURCE.feed_id = uf.feed_id
            AND ASOURCE.article_id = a.id
        )
    )
    WHERE uf.user_id = p_user_uuid;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER
SET search_path = content, public, extensions;

-- Function: content.articles_textsearchable_trigger()
-- Description: Auto-update textsearchable tsvector on title/summary/content changes
-- Security: SECURITY DEFINER - maintains full-text search index
CREATE OR REPLACE FUNCTION content.articles_textsearchable_trigger()
RETURNS TRIGGER AS $$
BEGIN
	NEW.textsearchable :=
		setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
		setweight(to_tsvector('english', COALESCE(NEW.summary, '')), 'B') ||
		setweight(to_tsvector('english', COALESCE(NEW.content, '')), 'C');
	RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER
SET search_path = content, public, extensions;

-- Trigger to auto-update textsearchable on INSERT/UPDATE of title/summary/content
DROP TRIGGER IF EXISTS trg_content_articles_textsearchable_update ON content.articles;
CREATE TRIGGER trg_content_articles_textsearchable_update
	BEFORE INSERT OR UPDATE OF title, summary, content
	ON content.articles
	FOR EACH ROW
	EXECUTE FUNCTION content.articles_textsearchable_trigger();

-- ================================================
-- PERMISSIONS
-- ================================================

-- Grant table permissions to app_service
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA content TO app_service;

-- Grant table permissions to app_readonly
GRANT SELECT ON ALL TABLES IN SCHEMA content TO app_readonly;

-- Grant sequence permissions to both roles
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA content TO app_service, app_readonly;

-- Grant execute permissions on trigger functions
GRANT EXECUTE ON FUNCTION content.update_user_feed_unread_count_on_read_change() TO app_service;
GRANT EXECUTE ON FUNCTION content.recalculate_user_feed_unread_count TO app_service;
GRANT EXECUTE ON FUNCTION content.recalculate_all_user_feed_unread_counts TO app_service;
GRANT EXECUTE ON FUNCTION content.articles_textsearchable_trigger() TO app_service;

-- ================================================
-- COMMENTS
-- ================================================

-- Feeds
COMMENT ON TABLE content.feeds IS 'Unified feed definitions for RSS/Atom feeds.';
COMMENT ON COLUMN content.feeds.title IS 'Feed title.';
COMMENT ON COLUMN content.feeds.description IS 'Feed description.';
COMMENT ON COLUMN content.feeds.feed_type IS 'Type of feed: rss or atom.';
COMMENT ON COLUMN content.feeds.language IS 'ISO language code of the feed content.';
COMMENT ON COLUMN content.feeds.website IS 'Website URL for the feed source.';
COMMENT ON COLUMN content.feeds.canonical_url IS 'URL of the RSS/Atom feed.';
COMMENT ON COLUMN content.feeds.latest_articles IS 'Array of the most recent article IDs for caching.';
COMMENT ON COLUMN content.feeds.last_update IS 'Timestamp of the most recent article from this source.';
COMMENT ON COLUMN content.feeds.last_fetched_at IS 'Timestamp of the last successful feed fetch.';
COMMENT ON COLUMN content.feeds.is_active IS 'Whether the feed is actively being fetched.';
COMMENT ON COLUMN content.feeds.error_count IS 'Consecutive fetch failures for monitoring.';
COMMENT ON COLUMN content.feeds.last_error IS 'Last error message encountered during fetch.';
COMMENT ON COLUMN content.feeds.last_error_at IS 'Timestamp of the last error.';

-- Articles
COMMENT ON TABLE content.articles IS 'Unified articles from feeds, deduplicated by canonical URL.';
COMMENT ON COLUMN content.articles.canonical_url IS 'Unique URL identifying the article.';
COMMENT ON COLUMN content.articles.title IS 'Article title.';
COMMENT ON COLUMN content.articles.author IS 'Author name.';
COMMENT ON COLUMN content.articles.summary IS 'Article summary/excerpt.';
COMMENT ON COLUMN content.articles.content IS 'Full HTML content from the feed.';
COMMENT ON COLUMN content.articles.textsearchable IS 'Stored tsvector for full-text search (title=A, summary=B, content=C weights). Auto-updated by trigger.';
COMMENT ON COLUMN content.articles.source_tags IS 'Tags/categories from the source.';
COMMENT ON COLUMN content.articles.media_url IS 'URL to the primary media image.';
COMMENT ON COLUMN content.articles.platform_metadata IS 'Platform-specific metadata (YouTube video ID, duration, views, etc.) stored as JSONB.';
COMMENT ON COLUMN content.articles.published_at IS 'Original publication timestamp.';

-- User Feeds
COMMENT ON TABLE content.user_feeds IS 'User subscriptions to feeds.';
COMMENT ON COLUMN content.user_feeds.user_id IS 'User who subscribed to this feed.';
COMMENT ON COLUMN content.user_feeds.feed_id IS 'Reference to the feed definition.';
COMMENT ON COLUMN content.user_feeds.title IS 'Custom title for the subscription (user override).';
COMMENT ON COLUMN content.user_feeds.is_pinned IS 'Whether the subscription is pinned to the top.';
COMMENT ON COLUMN content.user_feeds.is_active IS 'User-level toggle for the subscription.';
COMMENT ON COLUMN content.user_feeds.unread_count IS 'Cached count of unread articles.';
COMMENT ON COLUMN content.user_feeds.folder_id IS 'Folder for organizing the subscription.';
COMMENT ON COLUMN content.user_feeds.import_id IS 'OPML import that created this subscription, for rollback support.';

-- User Articles
COMMENT ON TABLE content.user_articles IS 'User-specific article states (read/unread, read later).';
COMMENT ON COLUMN content.user_articles.user_id IS 'User who owns this article state.';
COMMENT ON COLUMN content.user_articles.article_id IS 'Reference to the article.';
COMMENT ON COLUMN content.user_articles.is_read IS 'Whether the user has read this article.';
COMMENT ON COLUMN content.user_articles.read_at IS 'Timestamp when the article was marked as read.';
COMMENT ON COLUMN content.user_articles.read_later IS 'Whether the article is saved for later reading.';

-- Article Sources
COMMENT ON TABLE content.article_sources IS 'Junction table linking articles to their source feeds.';
COMMENT ON COLUMN content.article_sources.id IS 'Surrogate primary key for article sources.';
COMMENT ON COLUMN content.article_sources.article_id IS 'Reference to the article.';
COMMENT ON COLUMN content.article_sources.feed_id IS 'Reference to the feed that published this article.';
