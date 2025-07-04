"""Display Sublime Text Popup with marked input"""

from enum import Enum
from pathlib import Path
from typing import Union, Tuple

import sublime
import sublime_plugin

from .minihtml import html_to_minihtml
from .renderer import render_markdown, render_rst


class MarkupKind(Enum):
    PLAIN = "plain"
    MARKDOWN = "markdown"
    RE_STRUCTURED_TEXT = "reStructuredText"


RowCol = Tuple[int, int]

_RENDERER_MAP = {
    MarkupKind.PLAIN: lambda x: x,
    MarkupKind.MARKDOWN: render_markdown,
    MarkupKind.RE_STRUCTURED_TEXT: render_rst,
}


def render(text: str, kind: MarkupKind) -> str:
    """render text with selected kind"""
    return _RENDERER_MAP[kind](text)


css_style = Path(__file__).parent.joinpath("static/style.css").read_text()


def wrap_html_body(html_text: str) -> str:
    """add style"""
    return (
        '<body id="marked-popup">\n'
        f"<style>\n{css_style}\n</style>\n"
        f"{html_text}\n"
        "</body>"
    )


class MarkedPopupCommand(sublime_plugin.TextCommand):
    def run(
        self,
        edit: sublime.Edit,
        location: Union[int, RowCol],
        text: str,
        markup: str = "plain",
        keep_visible: bool = False,
    ):

        text = self.render_markup(text, markup)

        if isinstance(location, list):
            location = self.view.text_point(*location)

        flags = sublime.HIDE_ON_MOUSE_MOVE_AWAY | sublime.COOPERATE_WITH_AUTO_COMPLETE
        if keep_visible:
            flags |= sublime.KEEP_ON_SELECTION_MODIFIED

        self.view.show_popup(
            text,
            location=location,
            max_width=1024,
            flags=flags,
        )

    def render_markup(self, text: str, markup: str) -> str:
        if not text:
            return ""

        try:
            kind = MarkupKind(markup)
        except ValueError as err:
            message = f"markup must one of {[k.value for k in MarkupKind]}"
            raise ValueError(message) from err

        rendered_text = render(text, kind)
        return wrap_html_body(html_to_minihtml(rendered_text))
