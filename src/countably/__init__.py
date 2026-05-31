"""Lazy, immutable infinite sequences of numbers with element-wise arithmetic.

The primitives are :func:`constant` and :func:`count`; everything else is built
from them via arithmetic, comparison, rounding, slicing and the element-wise
:func:`maximum` and :func:`minimum` helpers.
"""

import importlib.metadata

from ._core import constant, count, maximum, minimum
from ._protocols import NumberSequence

__version__ = importlib.metadata.version(__name__)

__all__ = [
    "NumberSequence",
    "constant",
    "count",
    "maximum",
    "minimum",
    "__version__",
]
