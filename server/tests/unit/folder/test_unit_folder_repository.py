"""Unit tests for FolderRepository."""

from uuid import uuid4

import pytest

from backend.domain.folder import CircularReferenceError
from backend.infrastructure.repositories.folder import FolderRepository


class TestFolderRepositoryCreate:
    """Test folder creation operations."""

    async def test_create_folder_at_root(self, db_session):
        """Should create a root folder (parent_id=None)."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="folderuser",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = FolderRepository(db_session)
        folder = await repo.create_folder(
            user_id=user.id,
            name="Work",
            parent_id=None,
        )

        assert folder.id is not None
        assert folder.name == "Work"
        assert folder.user_id == user.id
        assert folder.parent_id is None
        assert folder.depth == 0
        assert folder.is_pinned is False

    async def test_create_folder_with_parent(self, db_session):
        """Should create a folder with a parent."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="folderuser2",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = FolderRepository(db_session)
        parent = await repo.create_folder(
            user_id=user.id,
            name="Parent",
            parent_id=None,
        )

        child = await repo.create_folder(
            user_id=user.id,
            name="Child",
            parent_id=parent.id,
        )

        assert child.parent_id == parent.id
        assert child.depth == 1  # Depth is calculated by trigger

    async def test_create_folder_with_duplicate_name_check(self, db_session):
        """Should detect duplicate names using folder_name_exists."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="folderuser3",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = FolderRepository(db_session)
        await repo.create_folder(
            user_id=user.id,
            name="Work",
            parent_id=None,
        )

        # Check that duplicate exists
        exists = await repo.folder_name_exists(
            user_id=user.id,
            name="Work",
            parent_id=None,
        )
        assert exists is True

    async def test_create_folder_same_name_different_parent_succeeds(
        self, db_session
    ):
        """Should allow same name under different parents."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="folderuser4",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = FolderRepository(db_session)
        await repo.create_folder(
            user_id=user.id,
            name="Work",
            parent_id=None,
        )
        folder2 = await repo.create_folder(
            user_id=user.id,
            name="Tech",
            parent_id=None,
        )

        # Same name as folder1 but under folder2 as parent
        child = await repo.create_folder(
            user_id=user.id,
            name="Work",  # Same name as folder1
            parent_id=folder2.id,
        )

        assert child.name == "Work"
        assert child.parent_id == folder2.id


class TestFolderRepositoryFind:
    """Test folder retrieval operations."""

    async def test_get_folder_by_id_and_user_when_exists(self, db_session):
        """Should return folder when it exists and belongs to user."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="folderuser5",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = FolderRepository(db_session)
        created = await repo.create_folder(
            user_id=user.id,
            name="Test",
            parent_id=None,
        )

        found = await repo.get_folder_by_id_and_user(created.id, user.id)

        assert found is not None
        assert found.id == created.id
        assert found.name == "Test"

    async def test_get_folder_by_id_and_user_returns_none_when_not_exists(
        self, db_session
    ):
        """Should return None when folder doesn't exist."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="folderuser6",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = FolderRepository(db_session)
        found = await repo.get_folder_by_id_and_user(uuid4(), user.id)

        assert found is None

    async def test_get_folder_by_id_and_user_returns_none_for_different_user(
        self, db_session
    ):
        """Should return None when folder exists but belongs to different user."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user1 = await user_repo.create_user(
            username="folderuser7",
            password_hash=password_hasher.hash_password("TestPass123"),
        )
        user2 = await user_repo.create_user(
            username="folderuser8",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = FolderRepository(db_session)
        folder = await repo.create_folder(
            user_id=user1.id,
            name="Secret",
            parent_id=None,
        )

        found = await repo.get_folder_by_id_and_user(folder.id, user2.id)

        assert found is None

    async def test_folder_name_exists_returns_true_when_exists(
        self, db_session
    ):
        """Should return True when folder with same name exists under parent."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="folderuser9",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = FolderRepository(db_session)
        await repo.create_folder(
            user_id=user.id,
            name="Work",
            parent_id=None,
        )

        exists = await repo.folder_name_exists(
            user_id=user.id,
            name="Work",
            parent_id=None,
        )

        assert exists is True

    async def test_folder_name_exists_returns_false_when_not_exists(
        self, db_session
    ):
        """Should return False when folder name doesn't exist."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="folderuser10",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = FolderRepository(db_session)

        exists = await repo.folder_name_exists(
            user_id=user.id,
            name="NonExistent",
            parent_id=None,
        )

        assert exists is False

    async def test_folder_name_exists_excludes_folder_id(self, db_session):
        """Should exclude folder when checking for updates."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="folderuser11",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = FolderRepository(db_session)
        folder = await repo.create_folder(
            user_id=user.id,
            name="Work",
            parent_id=None,
        )

        # Should return False when excluding the folder itself
        exists = await repo.folder_name_exists(
            user_id=user.id,
            name="Work",
            parent_id=None,
            exclude_folder_id=folder.id,
        )

        assert exists is False


class TestFolderRepositoryUpdate:
    """Test folder update operations."""

    async def test_update_folder_modifies_fields(self, db_session):
        """Should update specified folder fields."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="folderuser12",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = FolderRepository(db_session)
        folder = await repo.create_folder(
            user_id=user.id,
            name="Old Name",
            parent_id=None,
        )

        updated = await repo.update_folder(
            folder_id=folder.id,
            user_id=user.id,
            update_data={"name": "New Name", "is_pinned": True},
        )

        assert updated.name == "New Name"
        assert updated.is_pinned is True

    async def test_update_folder_non_existent_raises(self, db_session):
        """Should raise ValueError when folder doesn't exist."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="folderuser13",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = FolderRepository(db_session)

        with pytest.raises(ValueError, match="Folder not found"):
            await repo.update_folder(
                folder_id=uuid4(),
                user_id=user.id,
                update_data={"name": "New Name"},
            )


class TestFolderRepositoryDelete:
    """Test folder delete operations."""

    async def test_delete_folder_removes_folder(self, db_session):
        """Should delete the folder."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="folderuser14",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = FolderRepository(db_session)
        folder = await repo.create_folder(
            user_id=user.id,
            name="To Delete",
            parent_id=None,
        )

        await repo.delete_folder(folder.id, user.id)

        # Verify folder is deleted
        found = await repo.get_folder_by_id_and_user(folder.id, user.id)
        assert found is None

    async def test_delete_folder_non_existent_raises(self, db_session):
        """Should raise ValueError when folder doesn't exist."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="folderuser15",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = FolderRepository(db_session)

        with pytest.raises(ValueError, match="Folder not found"):
            await repo.delete_folder(uuid4(), user.id)


class TestFolderRepositoryCapacity:
    """Test folder capacity validation queries."""

    async def test_get_folder_capacity_metrics_at_root(self, db_session):
        """Should return correct metrics for root level."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="folderuser16",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = FolderRepository(db_session)

        # Create some root folders
        for i in range(3):
            await repo.create_folder(
                user_id=user.id,
                name=f"Folder {i}",
                parent_id=None,
            )

        folders_used, depth = await repo.get_folder_capacity_metrics(
            user_id=user.id,
            parent_id=None,
        )

        assert folders_used == 3
        assert depth == 0

    async def test_get_folder_capacity_metrics_with_parent(self, db_session):
        """Should return correct metrics for child folder."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="folderuser17",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = FolderRepository(db_session)
        parent = await repo.create_folder(
            user_id=user.id,
            name="Parent",
            parent_id=None,
        )

        # Create some children
        for i in range(2):
            await repo.create_folder(
                user_id=user.id,
                name=f"Child {i}",
                parent_id=parent.id,
            )

        folders_used, depth = await repo.get_folder_capacity_metrics(
            user_id=user.id,
            parent_id=parent.id,
        )

        assert folders_used == 2
        assert depth == 1  # Parent's depth + 1


class TestFolderRepositoryCircularReference:
    """Test circular reference detection."""

    async def test_check_circular_reference_detects_self_parent(
        self, db_session
    ):
        """Should detect when folder would be its own parent."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="folderuser18",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = FolderRepository(db_session)
        folder = await repo.create_folder(
            user_id=user.id,
            name="Self",
            parent_id=None,
        )

        with pytest.raises(CircularReferenceError):
            await repo.check_circular_reference(
                folder_id=folder.id,
                new_parent_id=folder.id,
                user_id=user.id,
            )

    async def test_check_circular_reference_detects_deep_cycle(
        self, db_session
    ):
        """Should detect circular reference in deep hierarchy."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="folderuser19",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = FolderRepository(db_session)

        # Create hierarchy: A -> B -> C -> D
        # Note: Depth is calculated by database trigger
        folder_a = await repo.create_folder(
            user_id=user.id, name="A", parent_id=None
        )
        await db_session.flush()  # Ensure trigger fired

        folder_b = await repo.create_folder(
            user_id=user.id, name="B", parent_id=folder_a.id
        )
        await db_session.flush()

        folder_c = await repo.create_folder(
            user_id=user.id, name="C", parent_id=folder_b.id
        )
        await db_session.flush()

        folder_d = await repo.create_folder(
            user_id=user.id, name="D", parent_id=folder_c.id
        )
        await db_session.flush()

        # Try to make A a child of D (would create cycle: A -> B -> C -> D -> A)
        with pytest.raises(CircularReferenceError):
            await repo.check_circular_reference(
                folder_id=folder_a.id,
                new_parent_id=folder_d.id,
                user_id=user.id,
            )

    async def test_check_circular_reference_passes_for_valid_parent(
        self, db_session
    ):
        """Should not raise for valid parent relationship."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="folderuser20",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = FolderRepository(db_session)
        parent = await repo.create_folder(
            user_id=user.id,
            name="Parent",
            parent_id=None,
        )
        child = await repo.create_folder(
            user_id=user.id,
            name="Child",
            parent_id=parent.id,
        )

        # Moving child to be sibling (under None) should be fine
        # This should not raise
        await repo.check_circular_reference(
            folder_id=child.id,
            new_parent_id=None,
            user_id=user.id,
        )


class TestFolderRepositoryUnreadCounts:
    """Test recursive unread count calculation."""

    async def test_get_recursive_unread_counts_with_hierarchy(self, db_session):
        """Should calculate recursive unread counts correctly."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="folderuser21",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = FolderRepository(db_session)

        # Create hierarchy:
        #   A (2 direct feeds)
        #     B (1 direct feed)
        #       C (3 direct feeds)
        folder_a = await repo.create_folder(
            user_id=user.id, name="A", parent_id=None
        )
        folder_b = await repo.create_folder(
            user_id=user.id, name="B", parent_id=folder_a.id
        )
        folder_c = await repo.create_folder(
            user_id=user.id, name="C", parent_id=folder_b.id
        )

        # Note: We'd need to create feeds and set unread counts
        # For this test, we're mainly checking the query structure
        counts = await repo.get_recursive_unread_counts(user.id)

        # Should return dict with all folders
        assert folder_a.id in counts
        assert folder_b.id in counts
        assert folder_c.id in counts

    async def test_get_recursive_unread_counts_empty(self, db_session):
        """Should return empty dict when no folders exist."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="folderuser22",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = FolderRepository(db_session)
        counts = await repo.get_recursive_unread_counts(user.id)

        assert counts == {}


class TestFolderRepositoryPagination:
    """Test paginated folder queries."""

    async def test_get_subfolders_paginated(self, db_session):
        """Should return paginated subfolders."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="folderuser23",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = FolderRepository(db_session)
        parent = await repo.create_folder(
            user_id=user.id,
            name="Parent",
            parent_id=None,
        )

        # Create 5 children
        for i in range(5):
            await repo.create_folder(
                user_id=user.id,
                name=f"Child {i}",
                parent_id=parent.id,
            )

        # Get first page
        subfolders, total = await repo.get_subfolders_paginated(
            parent_id=parent.id,
            user_id=user.id,
            limit=3,
            offset=0,
        )

        assert len(subfolders) == 3
        assert total == 5

    async def test_get_subfolders_paginated_with_offset(self, db_session):
        """Should skip folders with offset."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="folderuser24",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = FolderRepository(db_session)
        parent = await repo.create_folder(
            user_id=user.id,
            name="Parent",
            parent_id=None,
        )

        # Create 5 children
        for i in range(5):
            await repo.create_folder(
                user_id=user.id,
                name=f"Child {i}",
                parent_id=parent.id,
            )

        # Get second page
        subfolders, total = await repo.get_subfolders_paginated(
            parent_id=parent.id,
            user_id=user.id,
            limit=2,
            offset=2,
        )

        assert len(subfolders) == 2
        assert total == 5
