import importlib.metadata

from ._core import Sequence, constant, count

__version__ = importlib.metadata.version(__name__)

__all__ = ["Sequence", "constant", "count", "__version__"]
