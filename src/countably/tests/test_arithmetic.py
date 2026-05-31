"""Tests for element-wise arithmetic, unary ops, length, and immutability."""

import unittest
from dataclasses import FrozenInstanceError

from hamcrest import assert_that, raises

from countably import constant, count

from ._seq import (
    as_seq as _seq,
    assert_at,
    assert_infinite,
    assert_length,
    assert_prefix,
)


class TestAdd(unittest.TestCase):
    """Addition of sequences and numbers."""

    def test_two_constants(self) -> None:
        """Adding two constants yields a constant sum."""
        seq = constant(3) + constant(5)
        assert_at(seq, 0, 8)
        assert_at(seq, 100, 8)

    def test_constant_plus_count(self) -> None:
        """A constant plus count shifts the naturals."""
        assert_prefix(constant(3) + count(), [3, 4, 5, 6])

    def test_left_coerce(self) -> None:
        """A left-hand int is coerced before adding."""
        assert_prefix(3 + count(), [3, 4, 5, 6])

    def test_right_coerce(self) -> None:
        """A right-hand int is coerced before adding."""
        assert_prefix(count() + 3, [3, 4, 5, 6])


class TestSub(unittest.TestCase):
    """Subtraction of sequences and numbers."""

    def test_count_minus_one(self) -> None:
        """Subtracting one shifts the naturals down."""
        assert_prefix(count() - 1, [-1, 0, 1, 2])

    def test_left_coerce(self) -> None:
        """A left-hand int is coerced before subtracting."""
        assert_prefix(10 - count(), [10, 9, 8, 7])


class TestMul(unittest.TestCase):
    """Multiplication of sequences and numbers."""

    def test_count_times_two(self) -> None:
        """Multiplying count by two yields the even numbers."""
        assert_prefix(count() * 2, [0, 2, 4, 6])

    def test_left_coerce(self) -> None:
        """A left-hand int is coerced before multiplying."""
        assert_prefix(5 * count(), [0, 5, 10, 15])

    def test_complex_expression(self) -> None:
        """A mixed expression respects operator precedence."""
        assert_prefix(3 + 5 * count(), [3, 8, 13, 18])


class TestDiv(unittest.TestCase):
    """True and floor division of sequences and numbers."""

    def test_truediv(self) -> None:
        """True division produces floats."""
        assert_prefix((count() + 1) / 2, [0.5, 1.0, 1.5, 2.0])

    def test_truediv_left_coerce(self) -> None:
        """A left-hand int is coerced before true division."""
        assert_prefix(10 / (count() + 1), [10.0, 5.0, 10 / 3, 2.5])

    def test_floordiv(self) -> None:
        """Floor division truncates toward negative infinity."""
        assert_prefix(count() // 2, [0, 0, 1, 1, 2])

    def test_floordiv_left_coerce(self) -> None:
        """A left-hand int is coerced before floor division."""
        assert_prefix(10 // (count() + 1), [10, 5, 3, 2])


class TestMod(unittest.TestCase):
    """Modulo of sequences and numbers."""

    def test_mod(self) -> None:
        """Modulo cycles through the residues."""
        assert_prefix(count() % 3, [0, 1, 2, 0, 1, 2, 0])

    def test_mod_left_coerce(self) -> None:
        """A left-hand int is coerced before modulo."""
        assert_prefix(10 % (count() + 1), [0, 0, 1, 2, 0])


class TestPow(unittest.TestCase):
    """Exponentiation of sequences and numbers."""

    def test_pow(self) -> None:
        """Raising count to a power yields the squares."""
        assert_prefix(count() ** 2, [0, 1, 4, 9, 16])

    def test_pow_left_coerce(self) -> None:
        """A left-hand int base is coerced before exponentiation."""
        assert_prefix(2 ** count(), [1, 2, 4, 8, 16])


class TestUnary(unittest.TestCase):
    """Unary negation, posation, and absolute value."""

    def test_neg(self) -> None:
        """Negation flips the sign of every element."""
        assert_prefix(-count(), [0, -1, -2, -3])

    def test_pos(self) -> None:
        """Unary plus leaves elements unchanged."""
        assert_prefix(+(count() - 2), [-2, -1, 0, 1])

    def test_abs(self) -> None:
        """Absolute value folds negatives to positives."""
        assert_prefix(abs(count() - 2), [2, 1, 0, 1, 2])

    def test_unary_length_preserved(self) -> None:
        """A unary op preserves the length of a finite slice."""
        assert_length(-_seq(count()[2:10]), 8)

    def test_neg_index(self) -> None:
        """A negated sequence indexes to the negated element."""
        assert_at(-count(), 5, -5)

    def test_abs_index(self) -> None:
        """An absolute-value sequence indexes to the folded element."""
        seq = abs(count() - 3)
        assert_at(seq, 0, 3)
        assert_at(seq, 5, 2)


class TestLength(unittest.TestCase):
    """Combining sequences yields the length of the shorter operand."""

    def test_binop_infinite(self) -> None:
        """Combining two infinite sequences stays infinite."""
        assert_infinite(constant(3) + count())

    def test_binop_finite_takes_shorter(self) -> None:
        """Combining two finite slices takes the shorter length."""
        assert_length(_seq(count()[0:5]) + _seq(count()[0:3]), 3)

    def test_binop_finite_with_infinite(self) -> None:
        """Combining a finite slice with an infinite one is finite."""
        assert_length(_seq(count()[1:6]) + count(), 5)


class TestImmutability(unittest.TestCase):
    """Sequences are frozen, element-wise comparable, and unhashable."""

    def test_sequence_is_frozen(self) -> None:
        """Assigning to a sequence attribute raises FrozenInstanceError."""
        seq = constant(7)
        assert_that(
            lambda: setattr(seq, "computation", None),
            raises(FrozenInstanceError),
        )

    def test_elementwise_equality(self) -> None:
        """Equality is computed element-wise."""
        assert_prefix((3 + count()) == (3 + count()), [True] * 10)

    def test_elementwise_inequality(self) -> None:
        """Inequality is computed element-wise."""
        assert_prefix(count() != 2, [True, True, False, True, True])

    def test_not_hashable(self) -> None:
        """A sequence is not hashable."""
        assert_that(lambda: hash(constant(7)), raises(TypeError))
