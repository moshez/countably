"""Lazy, immutable infinite sequences of numbers with element-wise arithmetic.

The primitives are :func:`constant` and :func:`count`; everything else is
built from them via arithmetic, comparison, rounding, slicing and the
helpers :func:`maximum` / :func:`minimum`.
"""

import importlib.metadata

from ._core import NumberSequence, constant, count, maximum, minimum

__version__ = importlib.metadata.version(__name__)

__all__ = [
    "NumberSequence",
    "constant",
    "count",
    "maximum",
    "minimum",
    "__version__",
]
