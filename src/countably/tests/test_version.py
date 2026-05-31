"""Tests for the package version metadata."""

import unittest
from hamcrest import assert_that, contains_string

from countably import __version__


class TestVersion(unittest.TestCase):
    """The package exposes version metadata."""

    def test_has_dot(self) -> None:
        """The version string contains a dotted component."""
        assert_that(__version__, contains_string("."))
