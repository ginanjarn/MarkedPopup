"""renderer"""

import sys
from pathlib import Path

# Make library available to 'sys.path'
LIBRARY_PATH = str(Path(__file__).parent.joinpath("library"))
if LIBRARY_PATH not in sys.path:
    sys.path.append(LIBRARY_PATH)

import mistletoe
import docutils.core as docutils_core


def render_markdown(text: str) -> str:
    """render markdown script"""
    return mistletoe.markdown(text)


def render_rst(text: str) -> str:
    """render rst script"""
    return docutils_core.publish_parts(text, writer_name="html")["html_body"]
