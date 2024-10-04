"""Display Sublime Text Popup with marked input"""

from enum import Enum
from pathlib import Path
from typing import Union, Tuple

import sublime
import sublime_plugin

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


def _newline_to_br(text: str) -> str:
    return text.replace("\n", "<br>\n")


def _space_to_nbsp(text: str) -> str:
    return text.replace("  ", "&nbsp;&nbsp;")


def _hr_to_divclass_hr(text: str) -> str:
    return text.replace("<hr />", '<div class="hr"></div>')


def adapt_minihtml(html_text: str) -> str:
    """adapt html to Sublime minihtml implementation"""

    offset = 0
    temp = []

    while offset < len(html_text):
        op_text = "<pre"
        ed_text = "</pre>"

        op_index = html_text[offset:].find(op_text)
        if op_index < 0:
            break

        ed_index = html_text[offset:].find(ed_text)
        if ed_index < 0:
            break

        start = op_index + offset
        end = ed_index + offset

        prefix = html_text[offset:start]
        pre_body = html_text[start:end]
        adapted_pre_body = _newline_to_br(_space_to_nbsp(pre_body))
        temp.extend([prefix, adapted_pre_body, ed_text])
        offset = offset + end + len(ed_text)

    # else
    excess = html_text[offset:]
    temp.append(excess)

    new_text = "".join(temp)
    return _hr_to_divclass_hr(new_text)


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
        html_text = wrap_html_body(adapt_minihtml(rendered_text))
        self.view.show_popup(
            html_text,
            location=location,
            max_width=1024,
            flags=sublime.HIDE_ON_MOUSE_MOVE_AWAY
            | sublime.COOPERATE_WITH_AUTO_COMPLETE,
        )
