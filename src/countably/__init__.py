import importlib.metadata

from ._core import NumberSequence, constant, count

__version__ = importlib.metadata.version(__name__)

__all__ = ["NumberSequence", "constant", "count", "__version__"]
