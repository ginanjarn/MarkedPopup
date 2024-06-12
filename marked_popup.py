"""Display Sublime Text Popup with marked input"""

from enum import Enum
from pathlib import Path
from typing import Union, Tuple

import sublime
import sublime_plugin

from . import converter


class MarkupKind(Enum):
    PLAIN = "plain"
    MARKDOWN = "md"
    RE_STRUCTURED_TEXT = "rst"


RowCol = Tuple[int, int]

RENDERER = {
    MarkupKind.PLAIN: lambda x: x,
    MarkupKind.MARKDOWN: converter.convert_markdown,
    MarkupKind.RE_STRUCTURED_TEXT: converter.convert_rst,
}


def adapt_minihtml(text: str) -> str:
    """adapt regular html to minihtml"""

    offset = 0
    temp = []

    def normalize_space(text: str) -> str:
        # minihtml ignore '\n', force use '<br>\n'
        text = text.replace("\n", "<br>\n")
        # minihtml ignore space, force use '&nbsp;'
        text = text.replace("  ", "&nbsp;&nbsp;")
        return text

    while offset < len(text):
        op_text = "<pre"
        ed_text = "</pre>"

        op_index = text[offset:].find(op_text)
        if op_index < 0:
            break

        ed_index = text[offset:].find(ed_text)
        if ed_index < 0:
            break

        start = op_index + offset
        end = ed_index + offset

        prefix = text[offset:start]
        pre_body = text[start:end]
        temp.extend([prefix, normalize_space(pre_body), ed_text])
        offset = offset + end + len(ed_text)

    # else
    excess = text[offset:]
    temp.append(excess)

    return "".join(temp)


css_style = Path(__file__).parent.joinpath("static", "style.css").read_text()


def add_style(html_text: str) -> str:
    """add style"""
    return f"<body>\n<style>\n{css_style}\n</style>\n{html_text}\n</body>"


class MarkedPopup(sublime_plugin.TextCommand):
    def run(
        self,
        edit: sublime.Edit,
        location: Union[int, RowCol],
        text: str,
        markup: str = "PLAIN",
    ):
        if isinstance(location, list):
            location = self.view.text_point(location[0], location[1])

        try:
            kind = MarkupKind[markup.upper()]

        except KeyError:
            print(f"kind must in {[k.name for k in MarkupKind]}")
            return

        text = RENDERER[kind](text)
        if not text:
            return

        text = adapt_minihtml(text)
        text = add_style(text)

        self.view.show_popup(
            text,
            location=location,
            max_width=1024,
            flags=sublime.HIDE_ON_MOUSE_MOVE_AWAY
            | sublime.COOPERATE_WITH_AUTO_COMPLETE,
        )
