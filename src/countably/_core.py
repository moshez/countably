from __future__ import annotations

import functools
import itertools
import math
import sys
from dataclasses import dataclass
from typing import Callable, Iterator, Optional, Protocol, Self, TypeVar, Union

from ._protocols import NumberSequence, Number, SeqOrNumber, SliceArg

_BinOp = Callable[[Number, Number], Number]
_UnaryOp = Callable[[Number], Number]
_S = TypeVar("_S", bound="_Sequence")


class _Computation(Protocol):
    def __len__(self) -> int: ...

    def __getitem__(self, index: int) -> Number: ...

    def __iter__(self) -> Iterator[Number]: ...


@dataclass(frozen=True, slots=True, kw_only=True)
class _Cache:
    fn: Callable[[int], Number]

    @classmethod
    def for_computation(cls, computation: _Computation) -> "_Cache":
        """Wrap an LRU-memoized view of ``computation``'s element lookups.

        Args:
            computation: The computation whose ``__getitem__`` to memoize.

        Returns:
            A cache that returns memoized elements of ``computation``.
        """
        return cls(fn=functools.lru_cache(maxsize=100)(computation.__getitem__))

    def __call__(self, index: int) -> Number:
        return self.fn(index)


@dataclass(frozen=True, slots=True, kw_only=True, eq=False)
class _Sequence:
    computation: _Computation
    cache: _Cache

    __hash__ = None  # type: ignore[assignment]

    @classmethod
    def for_computation(cls, computation: _Computation) -> Self:
        """Build a sequence backed by ``computation`` and a fresh cache.

        Args:
            computation: The computation that produces the sequence's elements.

        Returns:
            A sequence whose elements come from ``computation``.
        """
        return cls(
            computation=computation,
            cache=_Cache.for_computation(computation),
        )

    def __len__(self) -> int:
        return len(self.computation)

    def __bool__(self) -> bool:
        raise TypeError("NumberSequence has no boolean value")

    def __str__(self) -> str:
        if len(self) == sys.maxsize:
            head = ", ".join(str(v) for v in itertools.islice(self, 5))
            return f"[{head}, ....]"
        return str(list(self))

    def __getitem__(self, index: Union[int, SliceArg]) -> Union[Number, Self]:
        if isinstance(index, slice):
            return _slice_sequence(self, index)
        size = len(self)
        position = index
        if position < 0:
            if size == sys.maxsize:
                raise IndexError("negative index on infinite sequence")
            position += size
        if position < 0 or position >= size:
            raise IndexError(index)
        return self.cache(position)

    def __iter__(self) -> Iterator[Number]:
        return iter(self.computation)

    def __add__(self, other: SeqOrNumber) -> Self:
        return _binop(type(self), self, other, lambda left, right: left + right)

    def __radd__(self, other: SeqOrNumber) -> Self:
        return _binop(type(self), other, self, lambda left, right: left + right)

    def __sub__(self, other: SeqOrNumber) -> Self:
        return _binop(type(self), self, other, lambda left, right: left - right)

    def __rsub__(self, other: SeqOrNumber) -> Self:
        return _binop(type(self), other, self, lambda left, right: left - right)

    def __mul__(self, other: SeqOrNumber) -> Self:
        return _binop(type(self), self, other, lambda left, right: left * right)

    def __rmul__(self, other: SeqOrNumber) -> Self:
        return _binop(type(self), other, self, lambda left, right: left * right)

    def __truediv__(self, other: SeqOrNumber) -> Self:
        return _binop(type(self), self, other, lambda left, right: left / right)

    def __rtruediv__(self, other: SeqOrNumber) -> Self:
        return _binop(type(self), other, self, lambda left, right: left / right)

    def __floordiv__(self, other: SeqOrNumber) -> Self:
        return _binop(type(self), self, other, lambda left, right: left // right)

    def __rfloordiv__(self, other: SeqOrNumber) -> Self:
        return _binop(type(self), other, self, lambda left, right: left // right)

    def __mod__(self, other: SeqOrNumber) -> Self:
        return _binop(type(self), self, other, lambda left, right: left % right)

    def __rmod__(self, other: SeqOrNumber) -> Self:
        return _binop(type(self), other, self, lambda left, right: left % right)

    def __pow__(self, other: SeqOrNumber) -> Self:
        return _binop(type(self), self, other, lambda left, right: left**right)

    def __rpow__(self, other: SeqOrNumber) -> Self:
        return _binop(type(self), other, self, lambda left, right: left**right)

    def __neg__(self) -> Self:
        return _unop(self, lambda value: -value)

    def __pos__(self) -> Self:
        return _unop(self, lambda value: +value)

    def __abs__(self) -> Self:
        return _unop(self, abs)

    def __eq__(self, other: SeqOrNumber) -> Self:  # type: ignore[override]
        return _binop(type(self), self, other, lambda left, right: left == right)

    def __ne__(self, other: SeqOrNumber) -> Self:  # type: ignore[override]
        return _binop(type(self), self, other, lambda left, right: left != right)

    def __lt__(self, other: SeqOrNumber) -> Self:
        return _binop(type(self), self, other, lambda left, right: left < right)

    def __le__(self, other: SeqOrNumber) -> Self:
        return _binop(type(self), self, other, lambda left, right: left <= right)

    def __gt__(self, other: SeqOrNumber) -> Self:
        return _binop(type(self), self, other, lambda left, right: left > right)

    def __ge__(self, other: SeqOrNumber) -> Self:
        return _binop(type(self), self, other, lambda left, right: left >= right)

    def __floor__(self) -> Self:
        return _unop(self, math.floor)

    def __ceil__(self) -> Self:
        return _unop(self, math.ceil)

    def __trunc__(self) -> Self:
        return _unop(self, math.trunc)

    def __round__(self, ndigits: Optional[int] = None) -> Self:
        def rounder(value: Number) -> Number:
            if ndigits is None:
                return round(value)
            return round(value, ndigits)

        return _unop(self, rounder)


@dataclass(frozen=True, slots=True, kw_only=True)
class _ConstantComputation:
    value: Number

    def __len__(self) -> int:
        return sys.maxsize

    def __getitem__(self, index: int) -> Number:
        return self.value

    def __iter__(self) -> Iterator[Number]:
        return itertools.repeat(self.value)


@dataclass(frozen=True, slots=True, kw_only=True)
class _CountComputation:
    def __len__(self) -> int:
        return sys.maxsize

    def __getitem__(self, index: int) -> Number:
        return index

    def __iter__(self) -> Iterator[Number]:
        return itertools.count()


@dataclass(frozen=True, slots=True, kw_only=True)
class _BinOpComputation:
    left: _Sequence
    right: _Sequence
    op: _BinOp

    def __len__(self) -> int:
        return min(len(self.left), len(self.right))

    def __getitem__(self, index: int) -> Number:
        return self.op(self.left.cache(index), self.right.cache(index))

    def __iter__(self) -> Iterator[Number]:
        return map(self.op, self.left, self.right)


@dataclass(frozen=True, slots=True, kw_only=True)
class _UnaryOpComputation:
    seq: _Sequence
    op: _UnaryOp

    def __len__(self) -> int:
        return len(self.seq)

    def __getitem__(self, index: int) -> Number:
        return self.op(self.seq.cache(index))

    def __iter__(self) -> Iterator[Number]:
        return map(self.op, self.seq)


@dataclass(frozen=True, slots=True, kw_only=True)
class _SlicedComputation:
    source: _Sequence
    start: int
    step: int
    length: int

    def __len__(self) -> int:
        return self.length

    def __getitem__(self, index: int) -> Number:
        return self.source.cache(self.start + self.step * index)

    def __iter__(self) -> Iterator[Number]:
        stop = (
            None if self.length == sys.maxsize else self.start + self.step * self.length
        )
        return itertools.islice(self.source, self.start, stop, self.step)


def _make_constant(value: Number) -> _Sequence:
    return _Sequence.for_computation(_ConstantComputation(value=value))


def _coerce(value: SeqOrNumber) -> _Sequence:
    if isinstance(value, _Sequence):
        return value
    if isinstance(value, (int, float)):
        return _make_constant(value)
    raise TypeError(  # pragma: no cover
        f"cannot coerce {type(value).__name__} to a NumberSequence"
    )


def _binop(typ: type[_S], left: SeqOrNumber, right: SeqOrNumber, op: _BinOp) -> _S:
    return typ.for_computation(
        _BinOpComputation(left=_coerce(left), right=_coerce(right), op=op)
    )


def _unop(seq: _S, op: _UnaryOp) -> _S:
    return type(seq).for_computation(_UnaryOpComputation(seq=seq, op=op))


def _slice_sequence(seq: _S, sl: SliceArg) -> _S:
    step = 1 if sl.step is None else sl.step
    start = 0 if sl.start is None else sl.start
    if step <= 0 or start < 0 or (sl.stop is not None and sl.stop < 0):
        raise ValueError(f"invalid slice: {sl!r}")
    source_len = len(seq)
    if sl.stop is None and source_len == sys.maxsize:
        length = sys.maxsize
    else:
        actual_stop = source_len if sl.stop is None else min(sl.stop, source_len)
        length = max(0, (actual_stop - start + step - 1) // step)
    return type(seq).for_computation(
        _SlicedComputation(source=seq, start=start, step=step, length=length)
    )


def constant(value: Number) -> NumberSequence:
    """Return an infinite sequence whose every element is ``value``.

    Args:
        value: The number repeated at every index of the sequence.

    Returns:
        An infinite sequence of ``value``.

    >>> from countably import constant
    >>> seq = constant(7)
    >>> seq[0], seq[1_000]
    (7, 7)
    """
    return _make_constant(value)


def count() -> NumberSequence:
    """Return the infinite sequence ``0, 1, 2, 3, ...``.

    The basic generator used to build everything else.

    Returns:
        The infinite sequence of the natural numbers.

    >>> from countably import count
    >>> list(count()[:5])
    [0, 1, 2, 3, 4]
    """
    return _Sequence.for_computation(_CountComputation())


def maximum(left: SeqOrNumber, right: SeqOrNumber) -> NumberSequence:
    """Return the element-wise maximum of two sequences (or sequence + number).

    Args:
        left: The first sequence or number to compare.
        right: The second sequence or number to compare.

    Returns:
        A sequence of the larger element at each position.

    >>> from countably import count, maximum
    >>> list(maximum(count(), 3)[:6])
    [3, 3, 3, 3, 4, 5]
    """
    return _binop(_Sequence, left, right, max)


def minimum(left: SeqOrNumber, right: SeqOrNumber) -> NumberSequence:
    """Return the element-wise minimum of two sequences (or sequence + number).

    Args:
        left: The first sequence or number to compare.
        right: The second sequence or number to compare.

    Returns:
        A sequence of the smaller element at each position.

    >>> from countably import count, minimum
    >>> list(minimum(count(), 3)[:6])
    [0, 1, 2, 3, 3, 3]
    """
    return _binop(_Sequence, left, right, min)
