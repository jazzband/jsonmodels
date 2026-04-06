from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("jsonmodels")
except PackageNotFoundError:
    __version__ = "unknown"
