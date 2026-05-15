from __future__ import annotations

import functools
import operator
import sys
from dataclasses import dataclass, field
from typing import Any, Callable, Iterator, Protocol, Union, final

Number = Union[int, float, complex]
SeqOrNumber = Union["Sequence", Number]


class Computation(Protocol):
    @property
    def length(self) -> int: ...

    def at(self, index: int) -> Any: ...


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class Sequence:
    _computation: Computation
    _cached_at: Any = field(init=False, repr=False, compare=False, default=None)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "_cached_at",
            functools.lru_cache(maxsize=100)(self._computation.at),
        )

    def __len__(self) -> int:
        return self._computation.length

    def __bool__(self) -> bool:
        raise TypeError("Sequence has no boolean value")

    def __getitem__(self, index: Union[int, slice]) -> Any:
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
        return self._cached_at(position)

    def __iter__(self) -> Iterator[Any]:
        size = len(self)
        position = 0
        while position < size:
            yield self[position]
            position += 1

    def __add__(self, other: SeqOrNumber) -> "Sequence":
        return _binop(self, other, operator.add)

    def __radd__(self, other: SeqOrNumber) -> "Sequence":
        return _binop(other, self, operator.add)

    def __sub__(self, other: SeqOrNumber) -> "Sequence":
        return _binop(self, other, operator.sub)

    def __rsub__(self, other: SeqOrNumber) -> "Sequence":
        return _binop(other, self, operator.sub)

    def __mul__(self, other: SeqOrNumber) -> "Sequence":
        return _binop(self, other, operator.mul)

    def __rmul__(self, other: SeqOrNumber) -> "Sequence":
        return _binop(other, self, operator.mul)

    def __truediv__(self, other: SeqOrNumber) -> "Sequence":
        return _binop(self, other, operator.truediv)

    def __rtruediv__(self, other: SeqOrNumber) -> "Sequence":
        return _binop(other, self, operator.truediv)

    def __floordiv__(self, other: SeqOrNumber) -> "Sequence":
        return _binop(self, other, operator.floordiv)

    def __rfloordiv__(self, other: SeqOrNumber) -> "Sequence":
        return _binop(other, self, operator.floordiv)

    def __mod__(self, other: SeqOrNumber) -> "Sequence":
        return _binop(self, other, operator.mod)

    def __rmod__(self, other: SeqOrNumber) -> "Sequence":
        return _binop(other, self, operator.mod)

    def __pow__(self, other: SeqOrNumber) -> "Sequence":
        return _binop(self, other, operator.pow)

    def __rpow__(self, other: SeqOrNumber) -> "Sequence":
        return _binop(other, self, operator.pow)

    def __neg__(self) -> "Sequence":
        return _unop(self, operator.neg)

    def __pos__(self) -> "Sequence":
        return _unop(self, operator.pos)

    def __abs__(self) -> "Sequence":
        return _unop(self, operator.abs)


@dataclass(frozen=True, slots=True, kw_only=True)
class _ConstantComputation:
    value: Any

    @property
    def length(self) -> int:
        return sys.maxsize

    def at(self, index: int) -> Any:
        return self.value


@dataclass(frozen=True, slots=True, kw_only=True)
class _CountComputation:
    @property
    def length(self) -> int:
        return sys.maxsize

    def at(self, index: int) -> int:
        return index


@dataclass(frozen=True, slots=True, kw_only=True)
class _BinOpComputation:
    left: Sequence
    right: Sequence
    op: Callable[[Any, Any], Any]

    @property
    def length(self) -> int:
        return min(len(self.left), len(self.right))

    def at(self, index: int) -> Any:
        return self.op(self.left[index], self.right[index])


@dataclass(frozen=True, slots=True, kw_only=True)
class _UnaryOpComputation:
    seq: Sequence
    op: Callable[[Any], Any]

    @property
    def length(self) -> int:
        return len(self.seq)

    def at(self, index: int) -> Any:
        return self.op(self.seq[index])


@dataclass(frozen=True, slots=True, kw_only=True)
class _SlicedComputation:
    source: Sequence
    start: int
    step: int
    length: int

    def at(self, index: int) -> Any:
        return self.source[self.start + self.step * index]


def _coerce(value: SeqOrNumber) -> Sequence:
    if isinstance(value, Sequence):
        return value
    return constant(value)


def _binop(
    left: SeqOrNumber,
    right: SeqOrNumber,
    op: Callable[[Any, Any], Any],
) -> Sequence:
    return Sequence(
        _computation=_BinOpComputation(left=_coerce(left), right=_coerce(right), op=op)
    )


def _unop(seq: Sequence, op: Callable[[Any], Any]) -> Sequence:
    return Sequence(_computation=_UnaryOpComputation(seq=seq, op=op))


def _slice_sequence(seq: Sequence, sl: slice) -> Sequence:
    if sl.step == 0:
        raise ValueError("slice step cannot be zero")
    step = 1 if sl.step is None else sl.step
    if step < 0:
        raise ValueError("negative step not supported")
    start = 0 if sl.start is None else sl.start
    if start < 0:
        raise ValueError("negative start not supported")
    source_len = len(seq)
    if sl.stop is None:
        stop = source_len
    else:
        if sl.stop < 0:
            raise ValueError("negative stop not supported")
        stop = min(sl.stop, source_len)
    if stop <= start:
        length = 0
    elif stop == sys.maxsize:
        length = sys.maxsize
    else:
        length = (stop - start + step - 1) // step
    return Sequence(
        _computation=_SlicedComputation(
            source=seq, start=start, step=step, length=length
        )
    )


def constant(value: Number) -> Sequence:
    return Sequence(_computation=_ConstantComputation(value=value))


def count() -> Sequence:
    return Sequence(_computation=_CountComputation())
