from __future__ import annotations

import functools
import itertools
import math
import operator
import sys
from dataclasses import dataclass, field
from typing import Callable, Iterator, Optional, Union

from ._protocols import NumberSequence, Number, SeqOrNumber, SliceArg, _Computation

_BinOp = Callable[[Number, Number], Number]
_UnaryOp = Callable[[Number], Number]


@dataclass(frozen=True, slots=True, kw_only=True)
class _Cache:
    fn: Callable[[int], Number]

    @classmethod
    def for_computation(cls, computation: _Computation) -> "_Cache":
        return cls(fn=functools.lru_cache(maxsize=100)(computation.__getitem__))

    def __call__(self, index: int) -> Number:
        return self.fn(index)


@dataclass(frozen=True, slots=True, kw_only=True)
class _Sequence:
    _computation: _Computation
    _cache: _Cache = field(compare=False)

    @classmethod
    def for_computation(cls, computation: _Computation) -> "_Sequence":
        return cls(
            _computation=computation,
            _cache=_Cache.for_computation(computation),
        )

    def __len__(self) -> int:
        return len(self._computation)

    def __bool__(self) -> bool:
        raise TypeError("NumberSequence has no boolean value")

    def __str__(self) -> str:
        if len(self) == sys.maxsize:
            head = ", ".join(str(v) for v in itertools.islice(self, 5))
            return f"[{head}, ....]"
        return str(list(self))

    def __getitem__(self, index: Union[int, SliceArg]) -> Union[Number, "_Sequence"]:
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
        return self._cache(position)

    def __iter__(self) -> Iterator[Number]:
        return iter(self._computation)

    def __add__(self, other: SeqOrNumber) -> "_Sequence":
        return _binop(self, other, operator.add)

    def __radd__(self, other: SeqOrNumber) -> "_Sequence":
        return _binop(other, self, operator.add)

    def __sub__(self, other: SeqOrNumber) -> "_Sequence":
        return _binop(self, other, operator.sub)

    def __rsub__(self, other: SeqOrNumber) -> "_Sequence":
        return _binop(other, self, operator.sub)

    def __mul__(self, other: SeqOrNumber) -> "_Sequence":
        return _binop(self, other, operator.mul)

    def __rmul__(self, other: SeqOrNumber) -> "_Sequence":
        return _binop(other, self, operator.mul)

    def __truediv__(self, other: SeqOrNumber) -> "_Sequence":
        return _binop(self, other, operator.truediv)

    def __rtruediv__(self, other: SeqOrNumber) -> "_Sequence":
        return _binop(other, self, operator.truediv)

    def __floordiv__(self, other: SeqOrNumber) -> "_Sequence":
        return _binop(self, other, operator.floordiv)

    def __rfloordiv__(self, other: SeqOrNumber) -> "_Sequence":
        return _binop(other, self, operator.floordiv)

    def __mod__(self, other: SeqOrNumber) -> "_Sequence":
        return _binop(self, other, operator.mod)

    def __rmod__(self, other: SeqOrNumber) -> "_Sequence":
        return _binop(other, self, operator.mod)

    def __pow__(self, other: SeqOrNumber) -> "_Sequence":
        return _binop(self, other, operator.pow)

    def __rpow__(self, other: SeqOrNumber) -> "_Sequence":
        return _binop(other, self, operator.pow)

    def __neg__(self) -> "_Sequence":
        return _unop(self, operator.neg)

    def __pos__(self) -> "_Sequence":
        return _unop(self, operator.pos)

    def __abs__(self) -> "_Sequence":
        return _unop(self, operator.abs)

    def __lt__(self, other: SeqOrNumber) -> "_Sequence":
        return _binop(self, other, operator.lt)

    def __le__(self, other: SeqOrNumber) -> "_Sequence":
        return _binop(self, other, operator.le)

    def __gt__(self, other: SeqOrNumber) -> "_Sequence":
        return _binop(self, other, operator.gt)

    def __ge__(self, other: SeqOrNumber) -> "_Sequence":
        return _binop(self, other, operator.ge)

    def __floor__(self) -> "_Sequence":
        return _unop(self, math.floor)

    def __ceil__(self) -> "_Sequence":
        return _unop(self, math.ceil)

    def __trunc__(self) -> "_Sequence":
        return _unop(self, math.trunc)

    def __round__(self, ndigits: Optional[int] = None) -> "_Sequence":
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
        return self.op(self.left._cache(index), self.right._cache(index))

    def __iter__(self) -> Iterator[Number]:
        return map(self.op, self.left, self.right)


@dataclass(frozen=True, slots=True, kw_only=True)
class _UnaryOpComputation:
    seq: _Sequence
    op: _UnaryOp

    def __len__(self) -> int:
        return len(self.seq)

    def __getitem__(self, index: int) -> Number:
        return self.op(self.seq._cache(index))

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
        return self.source._cache(self.start + self.step * index)

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


def _binop(left: SeqOrNumber, right: SeqOrNumber, op: _BinOp) -> _Sequence:
    return _Sequence.for_computation(
        _BinOpComputation(left=_coerce(left), right=_coerce(right), op=op)
    )


def _unop(seq: _Sequence, op: _UnaryOp) -> _Sequence:
    return _Sequence.for_computation(_UnaryOpComputation(seq=seq, op=op))


def _slice_sequence(seq: _Sequence, sl: SliceArg) -> _Sequence:
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
    return _Sequence.for_computation(
        _SlicedComputation(source=seq, start=start, step=step, length=length)
    )


def constant(value: Number) -> NumberSequence:
    """Return an infinite sequence whose every element is *value*.

    >>> from countably import constant
    >>> seq = constant(7)
    >>> seq[0], seq[1_000]
    (7, 7)
    """
    return _make_constant(value)


def count() -> NumberSequence:
    """Return the infinite sequence ``0, 1, 2, 3, ...``.

    The basic generator used to build everything else.

    >>> from countably import count
    >>> list(count()[:5])
    [0, 1, 2, 3, 4]
    """
    return _Sequence.for_computation(_CountComputation())


def maximum(left: SeqOrNumber, right: SeqOrNumber) -> NumberSequence:
    """Return the element-wise maximum of two sequences (or sequence + number).

    >>> from countably import count, maximum
    >>> list(maximum(count(), 3)[:6])
    [3, 3, 3, 3, 4, 5]
    """
    return _binop(left, right, max)


def minimum(left: SeqOrNumber, right: SeqOrNumber) -> NumberSequence:
    """Return the element-wise minimum of two sequences (or sequence + number).

    >>> from countably import count, minimum
    >>> list(minimum(count(), 3)[:6])
    [0, 1, 2, 3, 3, 3]
    """
    return _binop(left, right, min)
