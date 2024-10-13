"""Display Sublime Text Popup with marked input"""

from enum import Enum
from pathlib import Path
from typing import Union, Tuple

import sublime
import sublime_plugin

from .minihtml import html_to_minihtml
from . import converter


class MarkupKind(Enum):
    PLAIN = "plain"
    MARKDOWN = "markdown"
    RE_STRUCTURED_TEXT = "reStructuredText"


RowCol = Tuple[int, int]

_RENDERER = {
    MarkupKind.PLAIN: lambda x: x,
    MarkupKind.MARKDOWN: converter.convert_markdown,
    MarkupKind.RE_STRUCTURED_TEXT: converter.convert_rst,
}


def render(text: str, kind: MarkupKind) -> str:
    """render text with selected kind"""
    return _RENDERER[kind](text)


css_style = Path(__file__).parent.joinpath("static/style.css").read_text()


def wrap_html_body(html_text: str) -> str:
    """add style"""
    return (
        '<body id="marked-popup">\n'
        f"<style>\n{css_style}\n</style>\n"
        f"{html_text}\n"
        "</body>"
    )


class MarkedPopup(sublime_plugin.TextCommand):
    def run(
        self,
        edit: sublime.Edit,
        location: Union[int, RowCol],
        text: str,
        markup: str = "plain",
    ):
        if not text:
            return

        if isinstance(location, list):
            location = self.view.text_point(location[0], location[1])

        try:
            kind = MarkupKind(markup)
        except ValueError:
            print(f"kind must in {[k.value for k in MarkupKind]}")
            return

        rendered_text = render(text, kind)
        html_text = wrap_html_body(html_to_minihtml(rendered_text))
        self.view.show_popup(
            html_text,
            location=location,
            max_width=1024,
            flags=sublime.HIDE_ON_MOUSE_MOVE_AWAY
            | sublime.COOPERATE_WITH_AUTO_COMPLETE,
        )
