import importlib.metadata

from .brace_expand import brace_expand  # noqa: F401
from .errors import UnbalancedBracesError  # noqa: F401
from .glob import glob  # noqa: F401

__version__ = importlib.metadata.version(__name__)
