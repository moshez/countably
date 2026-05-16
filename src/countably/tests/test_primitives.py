import itertools
import sys
import unittest

from hamcrest import assert_that, equal_to, raises

from countably import NumberSequence, constant, count

from ._seq import as_seq as _seq


class TestConstant(unittest.TestCase):
    def test_value_at_zero(self) -> None:
        seq = constant(7)
        assert_that(seq[0], equal_to(7))

    def test_value_at_large_index(self) -> None:
        seq = constant(7)
        assert_that(seq[10_000], equal_to(7))

    def test_is_sequence(self) -> None:
        assert_that(isinstance(constant(7), NumberSequence), equal_to(True))

    def test_length_is_maxsize(self) -> None:
        assert_that(len(constant(7)), equal_to(sys.maxsize))

    def test_equality(self) -> None:
        assert_that(constant(7), equal_to(constant(7)))

    def test_iter(self) -> None:
        values = list(itertools.islice(constant(7), 4))
        assert_that(values, equal_to([7, 7, 7, 7]))


class TestCount(unittest.TestCase):
    def test_value_at_zero(self) -> None:
        assert_that(count()[0], equal_to(0))

    def test_value_at_index(self) -> None:
        assert_that(count()[42], equal_to(42))

    def test_length_is_maxsize(self) -> None:
        assert_that(len(count()), equal_to(sys.maxsize))

    def test_is_sequence(self) -> None:
        assert_that(isinstance(count(), NumberSequence), equal_to(True))

    def test_equality(self) -> None:
        assert_that(count(), equal_to(count()))

    def test_iter(self) -> None:
        values = list(itertools.islice(count(), 5))
        assert_that(values, equal_to([0, 1, 2, 3, 4]))


class TestBoolFails(unittest.TestCase):
    def test_bool_constant_raises(self) -> None:
        assert_that(lambda: bool(constant(7)), raises(TypeError))

    def test_bool_count_raises(self) -> None:
        assert_that(lambda: bool(count()), raises(TypeError))

    def test_bool_expression_raises(self) -> None:
        assert_that(lambda: bool(3 + count()), raises(TypeError))


class TestStr(unittest.TestCase):
    def test_infinite_count(self) -> None:
        assert_that(str(count()), equal_to("[0, 1, 2, 3, 4, ....]"))

    def test_infinite_constant(self) -> None:
        assert_that(str(constant(7)), equal_to("[7, 7, 7, 7, 7, ....]"))

    def test_finite_slice(self) -> None:
        assert_that(str(_seq(count()[2:5])), equal_to("[2, 3, 4]"))

    def test_empty_finite(self) -> None:
        assert_that(str(_seq(count()[5:3])), equal_to("[]"))


class TestIndexBounds(unittest.TestCase):
    def test_negative_index_on_infinite_raises(self) -> None:
        assert_that(lambda: count()[-1], raises(IndexError))

    def test_out_of_range_finite_raises(self) -> None:
        seq = _seq(count()[0:3])
        assert_that(lambda: seq[3], raises(IndexError))

    def test_finite_negative_index_works(self) -> None:
        seq = _seq(count()[2:10])
        assert_that(seq[-1], equal_to(9))

    def test_finite_negative_out_of_range_raises(self) -> None:
        seq = _seq(count()[2:5])
        assert_that(lambda: seq[-4], raises(IndexError))
