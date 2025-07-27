from .file import File, Folder
from .case import Case

import warnings

def my_formatwarning(message, category, filename, lineno, file=None, line=None):
    """
    Custom warning format for better readability.
    """
    return f"""{filename}, line {lineno}\n\t{category.__name__}: {message}\n"""

warnings.formatwarning = my_formatwarning

del my_formatwarning
del warnings

__all__ = [
    "File",
    "Folder",
    "Case",
]