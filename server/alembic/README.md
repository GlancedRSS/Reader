# Alembic Database Migrations

This project uses raw SQL migrations (no autogenerate) due to multi-schema foreign key constraints that break Alembic's autogenerate feature.

## Schemas

| Schema | Purpose |
|--------|---------|
| `accounts` | Identity profiles and user authentication |
| `content` | Feeds, articles, and user content interactions |
| `personalization` | User preferences, personal organization, and activity tracking |
| `management` | Data import/export utilities and system management |
| `extensions` | PostgreSQL extensions and utility functions |

## Creating Migrations

```bash
cd server && alembic revision -m "description"
```

Edit the generated file in `versions/` with raw SQL:

```python
from alembic import op

revision = '...'
down_revision = '...'

def upgrade() -> None:
    op.execute("""
        ALTER TABLE accounts.users ADD COLUMN bio TEXT;
        COMMENT ON COLUMN accounts.users.bio IS 'User bio';
    """)

def downgrade() -> None:
    op.execute("ALTER TABLE accounts.users DROP COLUMN bio;")
```

## Best Practices

1. **Schema-qualify all objects** - Use `accounts.users` not `users`
2. **Use `IF NOT EXISTS` / `IF EXISTS`** - Makes migrations idempotent
3. **Add `COMMENT ON`** - Document columns and tables
4. **Never modify existing migrations** - Create a new one instead
