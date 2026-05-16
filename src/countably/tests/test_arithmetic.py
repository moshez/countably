import sys
import unittest

from hamcrest import assert_that, equal_to, raises

from countably import constant, count

from ._seq import as_seq as _seq, take as _take


class TestAdd(unittest.TestCase):
    def test_two_constants(self) -> None:
        seq = constant(3) + constant(5)
        assert_that(seq[0], equal_to(8))
        assert_that(seq[100], equal_to(8))

    def test_constant_plus_count(self) -> None:
        seq = constant(3) + count()
        assert_that(_take(seq, 4), equal_to([3, 4, 5, 6]))

    def test_left_coerce(self) -> None:
        seq = 3 + count()
        assert_that(_take(seq, 4), equal_to([3, 4, 5, 6]))

    def test_right_coerce(self) -> None:
        seq = count() + 3
        assert_that(_take(seq, 4), equal_to([3, 4, 5, 6]))


class TestSub(unittest.TestCase):
    def test_count_minus_one(self) -> None:
        seq = count() - 1
        assert_that(_take(seq, 4), equal_to([-1, 0, 1, 2]))

    def test_left_coerce(self) -> None:
        seq = 10 - count()
        assert_that(_take(seq, 4), equal_to([10, 9, 8, 7]))


class TestMul(unittest.TestCase):
    def test_count_times_two(self) -> None:
        seq = count() * 2
        assert_that(_take(seq, 4), equal_to([0, 2, 4, 6]))

    def test_left_coerce(self) -> None:
        seq = 5 * count()
        assert_that(_take(seq, 4), equal_to([0, 5, 10, 15]))

    def test_complex_expression(self) -> None:
        seq = 3 + 5 * count()
        assert_that(_take(seq, 4), equal_to([3, 8, 13, 18]))


class TestDiv(unittest.TestCase):
    def test_truediv(self) -> None:
        seq = (count() + 1) / 2
        assert_that(_take(seq, 4), equal_to([0.5, 1.0, 1.5, 2.0]))

    def test_truediv_left_coerce(self) -> None:
        seq = 10 / (count() + 1)
        assert_that(_take(seq, 4), equal_to([10.0, 5.0, 10 / 3, 2.5]))

    def test_floordiv(self) -> None:
        seq = count() // 2
        assert_that(_take(seq, 5), equal_to([0, 0, 1, 1, 2]))

    def test_floordiv_left_coerce(self) -> None:
        seq = 10 // (count() + 1)
        assert_that(_take(seq, 4), equal_to([10, 5, 3, 2]))


class TestMod(unittest.TestCase):
    def test_mod(self) -> None:
        seq = count() % 3
        assert_that(_take(seq, 7), equal_to([0, 1, 2, 0, 1, 2, 0]))

    def test_mod_left_coerce(self) -> None:
        seq = 10 % (count() + 1)
        assert_that(_take(seq, 5), equal_to([0, 0, 1, 2, 0]))


class TestPow(unittest.TestCase):
    def test_pow(self) -> None:
        seq = count() ** 2
        assert_that(_take(seq, 5), equal_to([0, 1, 4, 9, 16]))

    def test_pow_left_coerce(self) -> None:
        seq = 2 ** count()
        assert_that(_take(seq, 5), equal_to([1, 2, 4, 8, 16]))


class TestUnary(unittest.TestCase):
    def test_neg(self) -> None:
        seq = -count()
        assert_that(_take(seq, 4), equal_to([0, -1, -2, -3]))

    def test_pos(self) -> None:
        seq = +(count() - 2)
        assert_that(_take(seq, 4), equal_to([-2, -1, 0, 1]))

    def test_abs(self) -> None:
        seq = abs(count() - 2)
        assert_that(_take(seq, 5), equal_to([2, 1, 0, 1, 2]))

    def test_unary_length_preserved(self) -> None:
        seq = -_seq(count()[2:10])
        assert_that(len(seq), equal_to(8))

    def test_neg_index(self) -> None:
        seq = -count()
        assert_that(seq[5], equal_to(-5))

    def test_abs_index(self) -> None:
        seq = abs(count() - 3)
        assert_that(seq[0], equal_to(3))
        assert_that(seq[5], equal_to(2))


class TestLength(unittest.TestCase):
    def test_binop_infinite(self) -> None:
        seq = constant(3) + count()
        assert_that(len(seq), equal_to(sys.maxsize))

    def test_binop_finite_takes_shorter(self) -> None:
        seq = _seq(count()[0:5]) + _seq(count()[0:3])
        assert_that(len(seq), equal_to(3))

    def test_binop_finite_with_infinite(self) -> None:
        seq = _seq(count()[0:5]) + count()
        assert_that(len(seq), equal_to(5))


class TestImmutability(unittest.TestCase):
    def test_sequence_is_frozen(self) -> None:
        from dataclasses import FrozenInstanceError

        seq = constant(7)
        assert_that(
            lambda: setattr(seq, "_computation", None),
            raises(FrozenInstanceError),
        )

    def test_elementwise_equality(self) -> None:
        first = 3 + count()
        second = 3 + count()
        assert_that(_take(first == second, 10), equal_to([True] * 10))

    def test_elementwise_inequality(self) -> None:
        seq = count() != 2
        assert_that(_take(seq, 5), equal_to([True, True, False, True, True]))

    def test_not_hashable(self) -> None:
        assert_that(lambda: hash(constant(7)), raises(TypeError))
