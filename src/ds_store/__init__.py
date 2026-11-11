from importlib.metadata import version

from .store import DSStore, DSStoreEntry

__version__ = version("ds_store")

__all__ = ["DSStore", "DSStoreEntry", "__version__"]
