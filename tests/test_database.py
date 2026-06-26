from unittest.mock import patch

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from database.models import Base, BlockedUser, User


@pytest.fixture
async def test_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def patched_db(test_engine):
    """Patch the database module to use an in-memory DB."""
    session_factory = async_sessionmaker(test_engine, expire_on_commit=False)
    with patch("database.db.engine", test_engine), patch(
        "database.db.SessionLocal", session_factory
    ):
        from database import db

        yield db


class TestGenderCompatible:
    def test_banned_candidate_rejected(self, make_user):
        from database.db import _gender_compatible

        searcher = make_user(telegram_id=1, gender="پسر")
        candidate = make_user(telegram_id=2, gender="دختر", banned=True)
        assert _gender_compatible(searcher, candidate) is False

    def test_no_gender_prefs_compatible(self, make_user):
        from database.db import _gender_compatible

        searcher = make_user(telegram_id=1)
        candidate = make_user(telegram_id=2)
        assert _gender_compatible(searcher, candidate) is True

    def test_searcher_wants_girl_candidate_is_girl(self, make_user):
        from database.db import _gender_compatible

        searcher = make_user(telegram_id=1, search_gender="دختر")
        candidate = make_user(telegram_id=2, gender="دختر")
        assert _gender_compatible(searcher, candidate) is True

    def test_searcher_wants_girl_candidate_is_boy(self, make_user):
        from database.db import _gender_compatible

        searcher = make_user(telegram_id=1, search_gender="دختر")
        candidate = make_user(telegram_id=2, gender="پسر")
        assert _gender_compatible(searcher, candidate) is False

    def test_candidate_wants_boy_searcher_is_boy(self, make_user):
        from database.db import _gender_compatible

        searcher = make_user(telegram_id=1, gender="پسر")
        candidate = make_user(telegram_id=2, search_gender="پسر")
        assert _gender_compatible(searcher, candidate) is True

    def test_candidate_wants_boy_searcher_is_girl(self, make_user):
        from database.db import _gender_compatible

        searcher = make_user(telegram_id=1, gender="دختر")
        candidate = make_user(telegram_id=2, search_gender="پسر")
        assert _gender_compatible(searcher, candidate) is False

    def test_candidate_wants_boy_searcher_no_gender(self, make_user):
        from database.db import _gender_compatible

        searcher = make_user(telegram_id=1, gender=None)
        candidate = make_user(telegram_id=2, search_gender="پسر")
        assert _gender_compatible(searcher, candidate) is False

    def test_both_prefer_each_other(self, make_user):
        from database.db import _gender_compatible

        searcher = make_user(telegram_id=1, gender="پسر", search_gender="دختر")
        candidate = make_user(telegram_id=2, gender="دختر", search_gender="پسر")
        assert _gender_compatible(searcher, candidate) is True

    def test_mutual_mismatch(self, make_user):
        from database.db import _gender_compatible

        searcher = make_user(telegram_id=1, gender="پسر", search_gender="دختر")
        candidate = make_user(telegram_id=2, gender="پسر", search_gender="دختر")
        assert _gender_compatible(searcher, candidate) is False


class TestSortCandidates:
    def test_vip_sorted_first(self, make_user):
        from database.db import _sort_candidates

        a = make_user(telegram_id=1, vip=False)
        b = make_user(telegram_id=2, vip=True)
        c = make_user(telegram_id=3, vip=False)
        result = _sort_candidates([a, b, c])
        assert result[0].telegram_id == 2

    def test_empty_list(self):
        from database.db import _sort_candidates

        assert _sort_candidates([]) == []

    def test_all_vip(self, make_user):
        from database.db import _sort_candidates

        a = make_user(telegram_id=1, vip=True)
        b = make_user(telegram_id=2, vip=True)
        result = _sort_candidates([a, b])
        assert len(result) == 2

    def test_no_vip(self, make_user):
        from database.db import _sort_candidates

        a = make_user(telegram_id=1, vip=False)
        b = make_user(telegram_id=2, vip=False)
        result = _sort_candidates([a, b])
        assert len(result) == 2


class TestAddUser:
    async def test_add_new_user(self, patched_db):
        user = await patched_db.add_user(telegram_id=1001, username="alice")
        assert user.telegram_id == 1001
        assert user.username == "alice"

    async def test_add_existing_user_returns_same(self, patched_db):
        await patched_db.add_user(telegram_id=1002, username="bob")
        user = await patched_db.add_user(telegram_id=1002, username="bob")
        assert user.telegram_id == 1002

    async def test_add_existing_user_updates_username(self, patched_db):
        await patched_db.add_user(telegram_id=1003, username="carol")
        user = await patched_db.add_user(telegram_id=1003, username="carol_new")
        assert user.username == "carol_new"

    async def test_add_user_with_none_username(self, patched_db):
        user = await patched_db.add_user(telegram_id=1004, username=None)
        assert user.username is None


class TestGetUser:
    async def test_get_existing_user(self, patched_db):
        await patched_db.add_user(telegram_id=2001, username="dave")
        user = await patched_db.get_user(2001)
        assert user is not None
        assert user.username == "dave"

    async def test_get_nonexistent_user(self, patched_db):
        user = await patched_db.get_user(9999)
        assert user is None


class TestBlockUser:
    async def test_block_and_check(self, patched_db):
        await patched_db.add_user(telegram_id=3001, username="u1")
        await patched_db.add_user(telegram_id=3002, username="u2")
        await patched_db.block_user(3001, 3002)
        assert await patched_db.is_blocked(3001, 3002) is True

    async def test_is_blocked_bidirectional(self, patched_db):
        await patched_db.add_user(telegram_id=3003, username="u3")
        await patched_db.add_user(telegram_id=3004, username="u4")
        await patched_db.block_user(3003, 3004)
        assert await patched_db.is_blocked(3004, 3003) is True

    async def test_not_blocked(self, patched_db):
        await patched_db.add_user(telegram_id=3005, username="u5")
        await patched_db.add_user(telegram_id=3006, username="u6")
        assert await patched_db.is_blocked(3005, 3006) is False

    async def test_duplicate_block_no_error(self, patched_db):
        await patched_db.add_user(telegram_id=3007, username="u7")
        await patched_db.add_user(telegram_id=3008, username="u8")
        await patched_db.block_user(3007, 3008)
        await patched_db.block_user(3007, 3008)
        assert await patched_db.is_blocked(3007, 3008) is True


class TestSetPartner:
    async def test_set_partner(self, patched_db):
        await patched_db.add_user(telegram_id=4001, username="x1")
        await patched_db.set_partner(4001, 4002)
        user = await patched_db.get_user(4001)
        assert user.partner_id == 4002
        assert user.is_searching is False

    async def test_set_partner_nonexistent_user(self, patched_db):
        await patched_db.set_partner(9999, 8888)


class TestEndChat:
    async def test_end_chat_clears_partner(self, patched_db):
        await patched_db.add_user(telegram_id=5001, username="c1")
        await patched_db.set_partner(5001, 5002)
        await patched_db.end_chat(5001)
        user = await patched_db.get_user(5001)
        assert user.partner_id is None
        assert user.is_searching is False

    async def test_end_chat_nonexistent_user(self, patched_db):
        await patched_db.end_chat(9999)


class TestStartSearching:
    async def test_start_searching(self, patched_db):
        await patched_db.add_user(telegram_id=6001, username="s1")
        await patched_db.start_searching(6001, "دختر")
        user = await patched_db.get_user(6001)
        assert user.is_searching is True
        assert user.search_gender == "دختر"
        assert user.partner_id is None

    async def test_start_searching_no_gender(self, patched_db):
        await patched_db.add_user(telegram_id=6002, username="s2")
        await patched_db.start_searching(6002)
        user = await patched_db.get_user(6002)
        assert user.is_searching is True
        assert user.search_gender is None


class TestCancelSearch:
    async def test_cancel_active_search(self, patched_db):
        await patched_db.add_user(telegram_id=7001, username="cs1")
        await patched_db.start_searching(7001)
        result = await patched_db.cancel_search(7001)
        assert result is True
        user = await patched_db.get_user(7001)
        assert user.is_searching is False

    async def test_cancel_not_searching(self, patched_db):
        await patched_db.add_user(telegram_id=7002, username="cs2")
        result = await patched_db.cancel_search(7002)
        assert result is False

    async def test_cancel_nonexistent_user(self, patched_db):
        result = await patched_db.cancel_search(9999)
        assert result is False

    async def test_cancel_with_partner_returns_false(self, patched_db):
        await patched_db.add_user(telegram_id=7003, username="cs3")
        await patched_db.start_searching(7003)
        await patched_db.set_partner(7003, 7004)
        result = await patched_db.cancel_search(7003)
        assert result is False


class TestSetBanned:
    async def test_ban_user(self, patched_db):
        await patched_db.add_user(telegram_id=8001, username="b1")
        result = await patched_db.set_banned(8001, True)
        assert result is True
        user = await patched_db.get_user(8001)
        assert user.banned is True
        assert user.is_searching is False

    async def test_unban_user(self, patched_db):
        await patched_db.add_user(telegram_id=8002, username="b2")
        await patched_db.set_banned(8002, True)
        result = await patched_db.set_banned(8002, False)
        assert result is True
        user = await patched_db.get_user(8002)
        assert user.banned is False

    async def test_ban_nonexistent_user(self, patched_db):
        result = await patched_db.set_banned(9999, True)
        assert result is False

    async def test_ban_clears_partner(self, patched_db):
        await patched_db.add_user(telegram_id=8003, username="b3")
        await patched_db.set_partner(8003, 8004)
        await patched_db.set_banned(8003, True)
        user = await patched_db.get_user(8003)
        assert user.partner_id is None


class TestSetVip:
    async def test_set_vip(self, patched_db):
        await patched_db.add_user(telegram_id=9001, username="v1")
        result = await patched_db.set_vip(9001, True)
        assert result is True
        user = await patched_db.get_user(9001)
        assert user.vip is True

    async def test_unset_vip(self, patched_db):
        await patched_db.add_user(telegram_id=9002, username="v2")
        await patched_db.set_vip(9002, True)
        result = await patched_db.set_vip(9002, False)
        assert result is True
        user = await patched_db.get_user(9002)
        assert user.vip is False

    async def test_set_vip_nonexistent(self, patched_db):
        result = await patched_db.set_vip(9999)
        assert result is False


class TestAddCoins:
    async def test_add_positive_coins(self, patched_db):
        await patched_db.add_user(telegram_id=10001, username="coin1")
        result = await patched_db.add_coins(10001, 50)
        assert result is True
        user = await patched_db.get_user(10001)
        assert user.coins == 50

    async def test_add_negative_coins_floors_at_zero(self, patched_db):
        await patched_db.add_user(telegram_id=10002, username="coin2")
        await patched_db.add_coins(10002, 10)
        result = await patched_db.add_coins(10002, -100)
        assert result is True
        user = await patched_db.get_user(10002)
        assert user.coins == 0

    async def test_add_coins_nonexistent_user(self, patched_db):
        result = await patched_db.add_coins(9999, 10)
        assert result is False


class TestIncrementReports:
    @patch("database.db.REPORTS_FOR_BAN", 3)
    async def test_increment_below_threshold(self, patched_db):
        await patched_db.add_user(telegram_id=11001, username="r1")
        reports = await patched_db.increment_reports(11001)
        assert reports == 1
        user = await patched_db.get_user(11001)
        assert user.banned is False

    @patch("database.db.REPORTS_FOR_BAN", 2)
    async def test_auto_ban_at_threshold(self, patched_db):
        await patched_db.add_user(telegram_id=11002, username="r2")
        await patched_db.increment_reports(11002)
        reports = await patched_db.increment_reports(11002)
        assert reports == 2
        user = await patched_db.get_user(11002)
        assert user.banned is True
        assert user.is_searching is False

    @patch("database.db.REPORTS_FOR_BAN", 2)
    async def test_auto_ban_clears_partner(self, patched_db):
        await patched_db.add_user(telegram_id=11003, username="r3")
        await patched_db.add_user(telegram_id=11004, username="r4")
        await patched_db.set_partner(11003, 11004)
        await patched_db.set_partner(11004, 11003)
        await patched_db.increment_reports(11003)
        await patched_db.increment_reports(11003)
        user = await patched_db.get_user(11003)
        assert user.partner_id is None
        partner = await patched_db.get_user(11004)
        assert partner.partner_id is None

    async def test_increment_nonexistent_user(self, patched_db):
        reports = await patched_db.increment_reports(9999)
        assert reports == 0


class TestGetStats:
    async def test_empty_stats(self, patched_db):
        stats = await patched_db.get_stats()
        assert stats["total"] == 0
        assert stats["searching"] == 0
        assert stats["in_chat"] == 0
        assert stats["banned"] == 0
        assert stats["vip"] == 0

    async def test_stats_with_users(self, patched_db):
        await patched_db.add_user(telegram_id=12001, username="st1")
        await patched_db.add_user(telegram_id=12002, username="st2")
        await patched_db.add_user(telegram_id=12003, username="st3")
        await patched_db.start_searching(12001)
        await patched_db.set_partner(12002, 12003)
        await patched_db.set_partner(12003, 12002)
        stats = await patched_db.get_stats()
        assert stats["total"] == 3
        assert stats["searching"] == 1
        assert stats["in_chat"] == 1


class TestGetAllTelegramIds:
    async def test_empty(self, patched_db):
        ids = await patched_db.get_all_telegram_ids()
        assert ids == []

    async def test_excludes_banned(self, patched_db):
        await patched_db.add_user(telegram_id=13001, username="all1")
        await patched_db.add_user(telegram_id=13002, username="all2")
        await patched_db.set_banned(13002, True)
        ids = await patched_db.get_all_telegram_ids()
        assert 13001 in ids
        assert 13002 not in ids
