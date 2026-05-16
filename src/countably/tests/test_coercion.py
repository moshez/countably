import unittest

from hamcrest import assert_that, equal_to

from countably import constant, count

from ._seq import take as _take


class TestCoercion(unittest.TestCase):
    def test_int_on_left_matches_explicit_constant(self) -> None:
        assert_that(3 + count(), equal_to(constant(3) + count()))

    def test_int_on_right_matches_explicit_constant(self) -> None:
        assert_that(count() + 3, equal_to(count() + constant(3)))

    def test_float_coerces(self) -> None:
        seq = 0.5 + count()
        assert_that(_take(seq, 3), equal_to([0.5, 1.5, 2.5]))

    def test_chained_coercion(self) -> None:
        seq = 3 + 5 * count()
        assert_that(_take(seq, 4), equal_to([3, 8, 13, 18]))

    def test_coerced_value_at_index(self) -> None:
        assert_that((10 - count())[3], equal_to(7))
