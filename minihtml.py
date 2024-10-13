MiniHTML = str
"""Custom HTML and CSS implemented in Sublime Text.

Similar to regular HTML and CSS with limited implementation. Implementation reference
in `https://www.sublimetext.com/docs/minihtml.html`.
"""


def html_to_minihtml(html_text: str) -> MiniHTML:
    """convert html to minihtml implementation"""

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


def _newline_to_br(text: str) -> str:
    return text.replace("\n", "<br>\n")


def _space_to_nbsp(text: str) -> str:
    return text.replace("  ", "&nbsp;&nbsp;")


def _hr_to_divclass_hr(text: str) -> str:
    return text.replace("<hr />", '<div class="hr"></div>')
