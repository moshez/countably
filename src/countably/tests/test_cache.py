import unittest

from hamcrest import assert_that, equal_to, greater_than_or_equal_to

from countably import count


class TestLRUCache(unittest.TestCase):
    def test_repeated_access_caches(self) -> None:
        seq = count() + 0
        first = seq[5]
        second = seq[5]
        assert_that(first, equal_to(second))
        info = seq._cached_at.cache_info()
        assert_that(info.hits, greater_than_or_equal_to(1))

    def test_cache_max_size_is_100(self) -> None:
        seq = count() + 0
        info = seq._cached_at.cache_info()
        assert_that(info.maxsize, equal_to(100))

    def test_cache_per_instance(self) -> None:
        first = count() + 0
        second = count() + 0
        _ = first[1]
        first_info = first._cached_at.cache_info()
        second_info = second._cached_at.cache_info()
        assert_that(first_info.currsize, equal_to(1))
        assert_that(second_info.currsize, equal_to(0))

    def test_cache_bounded(self) -> None:
        seq = count() + 0
        for index in range(150):
            _ = seq[index]
        info = seq._cached_at.cache_info()
        assert_that(info.currsize, equal_to(100))
