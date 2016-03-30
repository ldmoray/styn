"""
Lightweight Python Build Tool
"""

__version__ = "1.0.0"
__license__ = "MIT License"
__contact__ = "http://rags.github.com/pynt/"
from ._styn import chore, main
import pkgutil

__path__ = pkgutil.extend_path(__path__, __name__)

__all__ = ["chore", "main"]
