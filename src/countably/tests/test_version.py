import unittest
from hamcrest import assert_that, contains_string

from countably import __version__


class TestVersion(unittest.TestCase):
    def test_has_dot(self) -> None:
        assert_that(__version__, contains_string("."))
