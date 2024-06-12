"""coverter"""

import sys
from pathlib import Path
from typing import Callable

# Make library available to 'sys.path'
LIBRARY_PATH = str(Path(__file__).parent.joinpath("library"))
if LIBRARY_PATH not in sys.path:
    sys.path.append(LIBRARY_PATH)

import mistletoe
import docutils.core as docutils_core


def convert(marked: str, convert_func: Callable[[str], str]) -> str:
    """convert marked text to html"""
    return convert_func(marked)


def convert_markdown(text: str) -> str:
    """markdown renderer"""
    return mistletoe.markdown(text)


def convert_rst(text: str) -> str:
    """rst renderer"""
    return docutils_core.publish_parts(text, writer_name="html")["html_body"]
