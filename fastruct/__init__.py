# sourcery skip: use-contextlib-suppress
"""Init."""
from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("fastruct")
except PackageNotFoundError:
    # If the package is not installed, don't add __version__
    pass
