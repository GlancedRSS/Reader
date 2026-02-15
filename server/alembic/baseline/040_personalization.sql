-- =====================================================
-- 040_personalization.sql
-- User preferences, personal organization, and activity tracking
-- =====================================================

-- ================================================
-- USER PREFERENCES
-- ================================================

-- Table: personalization.user_preferences
-- Description: User account preferences for UI, feeds, and system settings
-- Relationships: One-to-one with accounts.users
CREATE TABLE IF NOT EXISTS personalization.user_preferences (
	user_id UUID PRIMARY KEY REFERENCES accounts.users(id) ON DELETE CASCADE,
	theme TEXT DEFAULT 'system',
	show_article_thumbnails BOOLEAN DEFAULT true,
	app_layout TEXT DEFAULT 'split',
	article_layout TEXT DEFAULT 'grid',
	font_spacing TEXT DEFAULT 'normal',
	font_size TEXT DEFAULT 'm',
	feed_sort_order TEXT DEFAULT 'recent_first',
	show_feed_favicons BOOLEAN DEFAULT true,
	date_format TEXT DEFAULT 'relative',
	time_format TEXT DEFAULT '12h',
	language TEXT NOT NULL DEFAULT 'en',
	auto_mark_as_read TEXT DEFAULT 'disabled',
	estimated_reading_time BOOLEAN DEFAULT true,
	show_summaries BOOLEAN DEFAULT true,
	created_at TIMESTAMPTZ DEFAULT NOW(),
	CONSTRAINT chk_personalization_user_preferences_theme CHECK (theme IN ('light', 'dark', 'system')),
	CONSTRAINT chk_personalization_user_preferences_app_layout CHECK (app_layout IN ('split', 'focus')),
	CONSTRAINT chk_personalization_user_preferences_article_layout CHECK (article_layout IN ('grid', 'list', 'magazine')),
	CONSTRAINT chk_personalization_user_preferences_font_spacing CHECK (font_spacing IN ('compact', 'normal', 'comfortable')),
	CONSTRAINT chk_personalization_user_preferences_font_size CHECK (font_size IN ('xs', 's', 'm', 'l', 'xl')),
	CONSTRAINT chk_personalization_user_preferences_feed_sort_order CHECK (feed_sort_order IN ('alphabetical', 'recent_first')),
	CONSTRAINT chk_personalization_user_preferences_date_format CHECK (date_format IN ('relative', 'absolute')),
	CONSTRAINT chk_personalization_user_preferences_time_format CHECK (time_format IN ('12h', '24h')),
	CONSTRAINT chk_personalization_user_preferences_language CHECK (language ~ '^[a-z]{2}(-[A-Z]{2})?$'),
	CONSTRAINT chk_personalization_user_preferences_auto_mark_as_read CHECK (auto_mark_as_read IN ('disabled', '7_days', '14_days', '30_days'))
);

-- ================================================
-- USER ORGANIZATION TOOLS
-- ================================================

-- Table: personalization.user_folders
-- Description: User-created folders for hierarchical feed organization
-- Relationships: Self-referencing hierarchy, parent of user_feeds
CREATE TABLE IF NOT EXISTS personalization.user_folders (
	id UUID DEFAULT extensions.gen_random_uuid() PRIMARY KEY,
	user_id UUID NOT NULL REFERENCES accounts.users(id) ON DELETE CASCADE,
	name VARCHAR(16) NOT NULL,
	parent_id UUID REFERENCES personalization.user_folders(id) ON DELETE SET NULL,
	is_pinned BOOLEAN DEFAULT false,
	depth INTEGER DEFAULT 0,
	created_at TIMESTAMPTZ DEFAULT NOW(),
	CONSTRAINT unique_user_folder_name UNIQUE (user_id, name, parent_id),
	CONSTRAINT chk_personalization_user_folders_depth CHECK (depth <= 9),
	CONSTRAINT chk_personalization_user_folders_name_not_empty CHECK (length(trim(name)) > 0)
);

-- Table: personalization.user_tags
-- Description: User-created tags for organizing and categorizing articles
-- Relationships: Many-to-many with articles through tags
CREATE TABLE IF NOT EXISTS personalization.user_tags (
	id UUID DEFAULT extensions.gen_random_uuid() PRIMARY KEY,
	user_id UUID REFERENCES accounts.users(id) ON DELETE CASCADE,
	name VARCHAR(64) NOT NULL,
	article_count INTEGER DEFAULT 0 NOT NULL,
	created_at TIMESTAMPTZ DEFAULT NOW(),
	CONSTRAINT unique_user_tag_name UNIQUE (user_id, name),
	CONSTRAINT chk_personalization_user_tags_article_count CHECK (article_count >= 0)
);

-- Table: personalization.tags
-- Description: Junction table linking user articles to user tags.
-- Relationships: Junction between content.user_articles and user_tags
CREATE TABLE IF NOT EXISTS personalization.tags (
	id UUID DEFAULT extensions.gen_random_uuid() PRIMARY KEY,
	user_article_id UUID NOT NULL REFERENCES content.user_articles(id) ON DELETE CASCADE,
	user_tag_id UUID NOT NULL REFERENCES personalization.user_tags(id) ON DELETE CASCADE,
	created_at TIMESTAMPTZ DEFAULT NOW(),
	UNIQUE(user_article_id, user_tag_id)
);


-- ================================================
-- INDEXES
-- ================================================

-- User folders indexes
CREATE INDEX IF NOT EXISTS idx_personalization_user_folders_user_id ON personalization.user_folders(user_id);
CREATE INDEX IF NOT EXISTS idx_personalization_user_folders_parent_id ON personalization.user_folders(parent_id);
CREATE INDEX IF NOT EXISTS idx_personalization_user_folders_pinned_sort ON personalization.user_folders(user_id, is_pinned DESC, name ASC);

-- User tags indexes
CREATE INDEX IF NOT EXISTS idx_personalization_user_tags_name ON personalization.user_tags(name);
CREATE INDEX IF NOT EXISTS idx_personalization_user_tags_user_id ON personalization.user_tags(user_id);

-- Tags indexes
CREATE INDEX IF NOT EXISTS idx_personalization_tags_user_article_id ON personalization.tags(user_article_id);
CREATE INDEX IF NOT EXISTS idx_personalization_tags_user_tag_id ON personalization.tags(user_tag_id);
CREATE INDEX IF NOT EXISTS idx_personalization_tags_user_tag_filter ON personalization.tags(user_tag_id) INCLUDE (user_article_id);

-- Production performance indexes
CREATE INDEX IF NOT EXISTS idx_personalization_user_folders_user_parent_optimized
ON personalization.user_folders(user_id, parent_id, depth);

CREATE INDEX IF NOT EXISTS idx_personalization_user_tags_user_name_optimized
ON personalization.user_tags(user_id, name)
WHERE name IS NOT NULL;

-- ================================================
-- TAG ARTICLE COUNT TRIGGERS
-- ================================================

-- Function: personalization.maintain_tag_article_count()
-- Description: Automatically maintains article_count on user_tags when tags are added/removed
-- Security: SECURITY DEFINER - maintains cached count integrity
CREATE OR REPLACE FUNCTION personalization.maintain_tag_article_count()
RETURNS TRIGGER AS $$
BEGIN
	IF TG_OP = 'INSERT' THEN
		-- Increment count when tag is added to an article
		UPDATE personalization.user_tags
		SET article_count = article_count + 1
		WHERE id = NEW.user_tag_id;
		RETURN NEW;
	ELSIF TG_OP = 'DELETE' THEN
		-- Decrement count when tag is removed from an article
		UPDATE personalization.user_tags
		SET article_count = GREATEST(article_count - 1, 0)
		WHERE id = OLD.user_tag_id;
		RETURN OLD;
	END IF;
	RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER
SET search_path = personalization, public, extensions;

-- Trigger to maintain article count on tag insert
DO $$
BEGIN
	IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_personalization_tags_maintain_count_insert') THEN
		CREATE TRIGGER trg_personalization_tags_maintain_count_insert
			AFTER INSERT ON personalization.tags
			FOR EACH ROW
			EXECUTE FUNCTION personalization.maintain_tag_article_count();
	END IF;
END $$;

-- Trigger to maintain article count on tag delete
DO $$
BEGIN
	IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_personalization_tags_maintain_count_delete') THEN
		CREATE TRIGGER trg_personalization_tags_maintain_count_delete
			AFTER DELETE ON personalization.tags
			FOR EACH ROW
			EXECUTE FUNCTION personalization.maintain_tag_article_count();
	END IF;
END $$;

-- ================================================
-- AUTO USER PREFERENCES TRIGGER
-- ================================================

-- Function: personalization.create_default_user_preferences()
-- Description: Automatically creates default user preferences when a user is created
-- Security: SECURITY DEFINER - inserts into user's private data
CREATE OR REPLACE FUNCTION personalization.create_default_user_preferences()
RETURNS TRIGGER AS $$
BEGIN
	INSERT INTO personalization.user_preferences (user_id)
	VALUES (NEW.id)
	ON CONFLICT (user_id) DO NOTHING;

	RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER
SET search_path = personalization, public, extensions;

-- Trigger to automatically create preferences when a new user account is created
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_accounts_users_create_preferences') THEN
        CREATE TRIGGER trg_accounts_users_create_preferences
            AFTER INSERT ON accounts.users
            FOR EACH ROW
            EXECUTE FUNCTION personalization.create_default_user_preferences();
    END IF;
END $$;

-- ================================================
-- FOLDER LIMITS ENFORCEMENT TRIGGERS
-- ================================================

-- Function: personalization.calculate_folder_depth()
-- Description: Automatically calculates folder depth and validates hierarchy
-- Security: SECURITY DEFINER - enforces business logic constraints
CREATE OR REPLACE FUNCTION personalization.calculate_folder_depth()
RETURNS TRIGGER AS $$
BEGIN
	IF NEW.parent_id IS NULL THEN
		NEW.depth := 0;
	ELSE
		IF NEW.parent_id = NEW.id THEN
			RAISE EXCEPTION 'Folder cannot be its own parent.';
		END IF;

		SELECT depth + 1 INTO NEW.depth
		FROM personalization.user_folders
		WHERE id = NEW.parent_id;

		IF NEW.depth > 9 THEN
			RAISE EXCEPTION 'Maximum folder nesting depth (10 levels) exceeded.';
		END IF;
	END IF;

	RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER
SET search_path = personalization, public, extensions;

-- Trigger to automatically calculate folder depth
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_personalization_user_folders_calculate_depth') THEN
        CREATE TRIGGER trg_personalization_user_folders_calculate_depth
            BEFORE INSERT OR UPDATE ON personalization.user_folders
            FOR EACH ROW
            EXECUTE FUNCTION personalization.calculate_folder_depth();
    END IF;
END $$;

-- Function: personalization.enforce_folder_limits()
-- Description: Enforces folder limits (max 50 sub-folders per parent)
-- Security: SECURITY DEFINER - enforces business logic constraints
CREATE OR REPLACE FUNCTION personalization.enforce_folder_limits()
RETURNS TRIGGER AS $$
DECLARE
	folder_count INTEGER;
	parent_user_id UUID;
BEGIN
	IF NEW.parent_id IS NULL THEN
		RETURN NEW;
	END IF;

	SELECT user_id INTO parent_user_id
	FROM personalization.user_folders
	WHERE id = NEW.parent_id;

	IF parent_user_id IS NULL THEN
		RAISE EXCEPTION 'Parent folder not found.';
	END IF;

	IF parent_user_id != NEW.user_id THEN
		RAISE EXCEPTION 'Folder parent must belong to the same user.';
	END IF;

	SELECT COUNT(*) INTO folder_count
	FROM personalization.user_folders
	WHERE parent_id = NEW.parent_id;

	IF folder_count >= 50 THEN
		RAISE EXCEPTION 'Maximum 50 sub-folders allowed per folder. Current count: %', folder_count;
	END IF;

	RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER
SET search_path = personalization, public, extensions;

-- Trigger to enforce folder limits before insertion
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_personalization_user_folders_enforce_limits') THEN
        CREATE TRIGGER trg_personalization_user_folders_enforce_limits
            BEFORE INSERT ON personalization.user_folders
            FOR EACH ROW
            EXECUTE FUNCTION personalization.enforce_folder_limits();
    END IF;
END $$;

-- Function: personalization.cascade_folder_depth()
-- Description: Recursively updates depth for all descendants when parent changes
-- Security: SECURITY DEFINER - maintains data integrity
CREATE OR REPLACE FUNCTION personalization.cascade_folder_depth()
RETURNS TRIGGER AS $$
DECLARE
	depth_diff INTEGER;
BEGIN
	-- Only proceed if parent_id actually changed
	IF OLD.parent_id IS NOT DISTINCT FROM NEW.parent_id THEN
		RETURN NEW;
	END IF;

	-- Calculate the depth difference for descendants
	-- NEW.depth has already been set by calculate_folder_depth() trigger
	depth_diff := NEW.depth - OLD.depth;

	-- If depth changed, update all descendants recursively
	IF depth_diff <> 0 THEN
		-- Update all descendants by adding the depth difference
		WITH RECURSIVE folder_tree AS (
			-- Start with direct children
			SELECT id, depth
			FROM personalization.user_folders
			WHERE parent_id = NEW.id

			UNION ALL

			-- Add grandchildren recursively
			SELECT f.id, f.depth
			FROM personalization.user_folders f
			INNER JOIN folder_tree ft ON f.parent_id = ft.id
		)
		UPDATE personalization.user_folders
		SET depth = depth + depth_diff
		WHERE id IN (SELECT id FROM folder_tree);
	END IF;

	RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER
SET search_path = personalization, public, extensions;

-- Trigger to cascade depth updates when parent_id changes
DO $$
BEGIN
	IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_personalization_user_folders_cascade_depth') THEN
		CREATE TRIGGER trg_personalization_user_folders_cascade_depth
			AFTER UPDATE OF parent_id ON personalization.user_folders
			FOR EACH ROW
			EXECUTE FUNCTION personalization.cascade_folder_depth();
	END IF;
END $$;

-- ================================================
-- TABLE PERMISSIONS
-- ================================================

-- Grant table permissions to app_service
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA personalization TO app_service;

-- Grant table permissions to app_readonly
GRANT SELECT ON ALL TABLES IN SCHEMA personalization TO app_readonly;

-- Grant sequence permissions to both roles
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA personalization TO app_service, app_readonly;

-- ================================================
-- CROSS-SCHEMA OPERATIONS
-- ================================================

-- Add folder_id column to content.user_feeds
ALTER TABLE content.user_feeds
ADD COLUMN IF NOT EXISTS folder_id UUID REFERENCES personalization.user_folders(id) ON DELETE SET NULL;

-- Add foreign key constraint for user_feeds.folder_id
DO $$
BEGIN
	IF NOT EXISTS (
		SELECT 1 FROM pg_constraint
		WHERE conname = 'fk_user_feeds_folder_id'
	) THEN
		ALTER TABLE content.user_feeds
		ADD CONSTRAINT fk_user_feeds_folder_id
		FOREIGN KEY (folder_id) REFERENCES personalization.user_folders(id) ON DELETE SET NULL;
	END IF;
END $$;

-- ================================================
-- COMMENTS
-- ================================================

-- User Preferences
COMMENT ON TABLE personalization.user_preferences IS 'User account preferences for UI, feeds, and system settings.';
COMMENT ON COLUMN personalization.user_preferences.theme IS 'UI theme: light, dark, or system preference.';
COMMENT ON COLUMN personalization.user_preferences.show_article_thumbnails IS 'Show thumbnails in article list.';
COMMENT ON COLUMN personalization.user_preferences.app_layout IS 'Application layout: split or focus mode.';
COMMENT ON COLUMN personalization.user_preferences.article_layout IS 'Article display layout: grid, list, or magazine.';
COMMENT ON COLUMN personalization.user_preferences.font_spacing IS 'Text spacing: compact, normal, or comfortable.';
COMMENT ON COLUMN personalization.user_preferences.font_size IS 'Font size: xs, s, m, l, or xl.';
COMMENT ON COLUMN personalization.user_preferences.feed_sort_order IS 'How feeds are sorted: alphabetical or recent first.';
COMMENT ON COLUMN personalization.user_preferences.show_feed_favicons IS 'Show feed favicons in the UI.';
COMMENT ON COLUMN personalization.user_preferences.date_format IS 'Date display format: relative or absolute.';
COMMENT ON COLUMN personalization.user_preferences.time_format IS 'Time display format: 12h or 24h.';
COMMENT ON COLUMN personalization.user_preferences.language IS 'Interface language code.';
COMMENT ON COLUMN personalization.user_preferences.auto_mark_as_read IS 'Auto-mark articles as read after: disabled, 7, 14, or 30 days.';
COMMENT ON COLUMN personalization.user_preferences.estimated_reading_time IS 'Show estimated reading time for articles.';
COMMENT ON COLUMN personalization.user_preferences.show_summaries IS 'Show article summaries in the feed.';

-- User Feed's Folder (cross-schema reference)
COMMENT ON COLUMN content.user_feeds.folder_id IS 'Folder for organizing the user feed subscription.';

-- User Folders
COMMENT ON TABLE personalization.user_folders IS 'User-created folders for hierarchical feed organization.';
COMMENT ON COLUMN personalization.user_folders.name IS 'Folder display name (max 16 characters).';
COMMENT ON COLUMN personalization.user_folders.parent_id IS 'Parent folder ID for hierarchical organization.';
COMMENT ON COLUMN personalization.user_folders.is_pinned IS 'Whether the folder is pinned to the top.';
COMMENT ON COLUMN personalization.user_folders.depth IS 'Nested depth level (0-9 for performance).';

-- User Tags
COMMENT ON TABLE personalization.user_tags IS 'User-created tags for organizing and categorizing articles.';
COMMENT ON COLUMN personalization.user_tags.name IS 'Tag display name (max 64 characters).';
COMMENT ON COLUMN personalization.user_tags.article_count IS 'Cached count of articles with this tag. Maintained by trigger.';

-- Tags (junction table)
COMMENT ON TABLE personalization.tags IS 'Junction table linking user articles to user tags.';
COMMENT ON COLUMN personalization.tags.id IS 'Surrogate primary key for tags.';
COMMENT ON COLUMN personalization.tags.user_article_id IS 'Reference to the user article.';
COMMENT ON COLUMN personalization.tags.user_tag_id IS 'Reference to the user tag.';
COMMENT ON COLUMN personalization.tags.created_at IS 'When the tag was applied to the article.';

-- Folder depth cascade function
COMMENT ON FUNCTION personalization.cascade_folder_depth() IS 'Cascades depth updates to all descendant folders when parent_id changes.';
