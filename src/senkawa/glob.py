import glob as g
import itertools
from collections.abc import Iterator

from .brace_expand import brace_expand


def glob(
    pathname: str,
    *,
    root_dir: str | None = None,
    dir_fd: int | None = None,
    recursive: bool = False,
    escape: bool = False,
    **kwargs,
) -> Iterator[str]:
    """Glob with brace expansion.

    Args:
        pathname (str): A pathname to glob.
        root_dir (str | None, optional): A root directory. Defaults to None.
        dir_fd (int | None, optional): A directory file descriptor. Defaults to None.
        recursive (bool, optional): Whether to do recursive glob or not. Defaults to False.
        escape (bool, optional): Whether to allow escaping special characters for brace expansion by a backslash or not. Defaults to True.

    Yields:
        Iterator[str]: An iterator over strings resulting from glob and brace expansion.
    """  # noqa: E501
    brace_expanded = brace_expand(pathname, escape=escape)
    glob_expanded = [
        g.glob(
            p,
            root_dir=root_dir,
            dir_fd=dir_fd,
            recursive=recursive,
            **kwargs,
        )
        for p in brace_expanded
    ]
    return itertools.chain.from_iterable(glob_expanded)
