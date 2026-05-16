from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Iterator,
    Optional,
    Protocol,
    Self,
    TypeAlias,
    Union,
    runtime_checkable,
)

Number = float
SeqOrNumber = Union["NumberSequence", Number]
if TYPE_CHECKING:
    SliceArg: TypeAlias = slice[Optional[int], Optional[int], Optional[int]]
else:
    SliceArg = slice


class _Computation(Protocol):
    def __len__(self) -> int: ...

    def __getitem__(self, index: int) -> Number: ...

    def __iter__(self) -> Iterator[Number]: ...


@runtime_checkable
class NumberSequence(Protocol):
    """A lazy, immutable sequence of numbers with element-wise arithmetic.

    Instances are produced by :func:`countably.constant` and
    :func:`countably.count`; everything else is built from them via arithmetic
    (``+``, ``-``, ``*``, ``/``, ``//``, ``%``, ``**``), comparisons
    (``<``, ``<=``, ``>``, ``>=``), unary ops (``-x``, ``abs(x)``), rounding
    (:func:`math.floor`, :func:`math.ceil`, :func:`math.trunc`,
    :func:`round`), slicing, and the element-wise helpers
    :func:`countably.maximum` / :func:`countably.minimum`.

    Sequences are *iterable*, not iterators: ``iter(seq)`` starts a fresh
    walk each time. Infinite sequences report :data:`sys.maxsize` from
    :func:`len`; finite slices report their true length. :func:`bool`
    deliberately raises :class:`TypeError` -- the truth value of a
    (possibly infinite) sequence is not defined.
    """

    def __len__(self) -> int: ...

    def __bool__(self) -> bool: ...

    def __getitem__(self, index: Union[int, SliceArg]) -> Union[Number, Self]: ...

    def __iter__(self) -> Iterator[Number]: ...

    def __add__(self, other: SeqOrNumber) -> Self: ...

    def __radd__(self, other: SeqOrNumber) -> Self: ...

    def __sub__(self, other: SeqOrNumber) -> Self: ...

    def __rsub__(self, other: SeqOrNumber) -> Self: ...

    def __mul__(self, other: SeqOrNumber) -> Self: ...

    def __rmul__(self, other: SeqOrNumber) -> Self: ...

    def __truediv__(self, other: SeqOrNumber) -> Self: ...

    def __rtruediv__(self, other: SeqOrNumber) -> Self: ...

    def __floordiv__(self, other: SeqOrNumber) -> Self: ...

    def __rfloordiv__(self, other: SeqOrNumber) -> Self: ...

    def __mod__(self, other: SeqOrNumber) -> Self: ...

    def __rmod__(self, other: SeqOrNumber) -> Self: ...

    def __pow__(self, other: SeqOrNumber) -> Self: ...

    def __rpow__(self, other: SeqOrNumber) -> Self: ...

    def __neg__(self) -> Self: ...

    def __pos__(self) -> Self: ...

    def __abs__(self) -> Self: ...

    def __eq__(self, other: SeqOrNumber) -> Self: ...  # type: ignore[override]

    def __ne__(self, other: SeqOrNumber) -> Self: ...  # type: ignore[override]

    def __lt__(self, other: SeqOrNumber) -> Self: ...

    def __le__(self, other: SeqOrNumber) -> Self: ...

    def __gt__(self, other: SeqOrNumber) -> Self: ...

    def __ge__(self, other: SeqOrNumber) -> Self: ...

    def __floor__(self) -> Self: ...

    def __ceil__(self) -> Self: ...

    def __trunc__(self) -> Self: ...

    def __round__(self, ndigits: Optional[int] = None) -> Self: ...
