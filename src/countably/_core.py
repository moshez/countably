from __future__ import annotations

import functools
import itertools
import operator
import sys
from dataclasses import dataclass
from typing import (
    Any,
    Callable,
    Generic,
    Iterator,
    Protocol,
    TypeVar,
    Union,
    final,
    overload,
)

Number = Union[int, float, complex]
SeqOrNumber = Union["Sequence[Any]", Number]

T_co = TypeVar("T_co", covariant=True)
T = TypeVar("T", int, float, complex)


class Computation(Protocol[T_co]):
    def __len__(self) -> int: ...

    def __getitem__(self, index: int) -> T_co: ...

    def __iter__(self) -> Iterator[T_co]: ...


@final
@dataclass(frozen=True, kw_only=True)
class Sequence(Generic[T_co]):
    _computation: Computation[T_co]

    @functools.cached_property
    def _cached_at(self) -> Any:
        return functools.lru_cache(maxsize=100)(self._computation.__getitem__)

    def __len__(self) -> int:
        return len(self._computation)

    def __bool__(self) -> bool:
        raise TypeError("Sequence has no boolean value")

    @overload
    def __getitem__(self, index: int) -> T_co: ...

    @overload
    def __getitem__(self, index: slice) -> "Sequence[T_co]": ...

    def __getitem__(self, index: Union[int, slice]) -> Union[T_co, "Sequence[T_co]"]:
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

    def __iter__(self) -> Iterator[T_co]:
        return iter(self._computation)

    def __add__(self, other: SeqOrNumber) -> "Sequence[Number]":
        return _binop(self, other, operator.add)

    def __radd__(self, other: SeqOrNumber) -> "Sequence[Number]":
        return _binop(other, self, operator.add)

    def __sub__(self, other: SeqOrNumber) -> "Sequence[Number]":
        return _binop(self, other, operator.sub)

    def __rsub__(self, other: SeqOrNumber) -> "Sequence[Number]":
        return _binop(other, self, operator.sub)

    def __mul__(self, other: SeqOrNumber) -> "Sequence[Number]":
        return _binop(self, other, operator.mul)

    def __rmul__(self, other: SeqOrNumber) -> "Sequence[Number]":
        return _binop(other, self, operator.mul)

    def __truediv__(self, other: SeqOrNumber) -> "Sequence[Number]":
        return _binop(self, other, operator.truediv)

    def __rtruediv__(self, other: SeqOrNumber) -> "Sequence[Number]":
        return _binop(other, self, operator.truediv)

    def __floordiv__(self, other: SeqOrNumber) -> "Sequence[Number]":
        return _binop(self, other, operator.floordiv)

    def __rfloordiv__(self, other: SeqOrNumber) -> "Sequence[Number]":
        return _binop(other, self, operator.floordiv)

    def __mod__(self, other: SeqOrNumber) -> "Sequence[Number]":
        return _binop(self, other, operator.mod)

    def __rmod__(self, other: SeqOrNumber) -> "Sequence[Number]":
        return _binop(other, self, operator.mod)

    def __pow__(self, other: SeqOrNumber) -> "Sequence[Number]":
        return _binop(self, other, operator.pow)

    def __rpow__(self, other: SeqOrNumber) -> "Sequence[Number]":
        return _binop(other, self, operator.pow)

    def __neg__(self) -> "Sequence[Number]":
        return _unop(self, operator.neg)

    def __pos__(self) -> "Sequence[Number]":
        return _unop(self, operator.pos)

    def __abs__(self) -> "Sequence[Number]":
        return _unop(self, operator.abs)


@dataclass(frozen=True, slots=True, kw_only=True)
class _ConstantComputation(Generic[T]):
    value: T

    def __len__(self) -> int:
        return sys.maxsize

    def __getitem__(self, index: int) -> T:
        return self.value

    def __iter__(self) -> Iterator[T]:
        return itertools.repeat(self.value)


@dataclass(frozen=True, slots=True, kw_only=True)
class _CountComputation:
    def __len__(self) -> int:
        return sys.maxsize

    def __getitem__(self, index: int) -> int:
        return index

    def __iter__(self) -> Iterator[int]:
        return itertools.count()


@dataclass(frozen=True, slots=True, kw_only=True)
class _BinOpComputation:
    left: Sequence[Number]
    right: Sequence[Number]
    op: Callable[[Number, Number], Number]

    def __len__(self) -> int:
        return min(len(self.left), len(self.right))

    def __getitem__(self, index: int) -> Number:
        return self.op(self.left[index], self.right[index])

    def __iter__(self) -> Iterator[Number]:
        return map(self.op, self.left, self.right)


@dataclass(frozen=True, slots=True, kw_only=True)
class _UnaryOpComputation:
    seq: Sequence[Number]
    op: Callable[[Number], Number]

    def __len__(self) -> int:
        return len(self.seq)

    def __getitem__(self, index: int) -> Number:
        return self.op(self.seq[index])

    def __iter__(self) -> Iterator[Number]:
        return map(self.op, self.seq)


@dataclass(frozen=True, slots=True, kw_only=True)
class _SlicedComputation(Generic[T_co]):
    source: Sequence[T_co]
    start: int
    step: int
    length: int

    def __len__(self) -> int:
        return self.length

    def __getitem__(self, index: int) -> T_co:
        return self.source[self.start + self.step * index]

    def __iter__(self) -> Iterator[T_co]:
        stop = (
            None if self.length == sys.maxsize else self.start + self.step * self.length
        )
        return itertools.islice(self.source, self.start, stop, self.step)


def _coerce(value: SeqOrNumber) -> Sequence[Number]:
    if isinstance(value, Sequence):
        return value
    return constant(value)


def _binop(
    left: SeqOrNumber,
    right: SeqOrNumber,
    op: Callable[[Number, Number], Number],
) -> Sequence[Number]:
    return Sequence(
        _computation=_BinOpComputation(left=_coerce(left), right=_coerce(right), op=op)
    )


def _unop(
    seq: Sequence[Any],
    op: Callable[[Number], Number],
) -> Sequence[Number]:
    return Sequence(_computation=_UnaryOpComputation(seq=seq, op=op))


def _slice_sequence(seq: Sequence[T_co], sl: slice) -> Sequence[T_co]:
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
    return Sequence(
        _computation=_SlicedComputation(
            source=seq, start=start, step=step, length=length
        )
    )


def constant(value: T) -> Sequence[T]:
    return Sequence(_computation=_ConstantComputation(value=value))


def count() -> Sequence[int]:
    return Sequence(_computation=_CountComputation())
