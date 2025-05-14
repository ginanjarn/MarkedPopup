"""MiniHTML adapter"""

from html import escape
from html.parser import HTMLParser
from typing import List


MiniHTML = str
"""Custom HTML and CSS implemented in Sublime Text.

Similar to regular HTML and CSS with limited implementation. Implementation reference
in `https://www.sublimetext.com/docs/minihtml.html`.
"""


def _newline_to_br(text: str) -> str:
    lines = text.splitlines(keepends=True)
    return "<br>".join(lines)


def _space_to_nbsp(text: str) -> str:
    return text.replace("  ", "&nbsp;&nbsp;")


class MiniHTMLElementParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)

        self.elements: List[str] = []
        self._enter_pre_tag = False

    def handle_startendtag(self, tag, attrs):
        """Similar to handle_starttag(), but called when the parser encounters an
        XHTML-style empty tag (<img ... />). This method may be overridden by
        subclasses which require this particular lexical information; the default
        implementation simply calls handle_starttag() and handle_endtag()."""

        if tag == "hr":
            # <hr> is not supported by minihtml
            self.elements.append('<div class="hr"></div>')
            return

        tag_elements = [tag] + [f'{k}="{escape(v)}"' for k, v in attrs]
        self.elements.append(f"<{' '.join(tag_elements)}>")

    def handle_starttag(self, tag, attrs):
        """This method is called to handle the start tag of an element (e.g. <div id="main">).

        The tag argument is the name of the tag converted to lower case.
        The attrs argument is a list of (name, value) pairs containing
        the attributes found inside the tag’s <> brackets.
        The name will be translated to lower case, and quotes in the value have been removed,
        and character and entity references have been replaced.

        For instance, for the tag <A HREF="https://www.cwi.nl/">, this method would
        be called as handle_starttag('a', [('href', 'https://www.cwi.nl/')]).

        All entity references from html.entities are replaced in the attribute values."""

        tag_elements = [tag] + [f'{k}="{escape(v)}"' for k, v in attrs]
        self.elements.append(f"<{' '.join(tag_elements)}>")

        if tag == "pre":
            # enter pre tag
            self._enter_pre_tag = True

    def handle_endtag(self, tag):
        """This method is called to handle the end tag of an element (e.g. </div>).

        The tag argument is the name of the tag converted to lower case."""

        self.elements.append(f"</{tag}>")

        if tag == "pre":
            # exit pre tag
            self._enter_pre_tag = False

    def handle_charref(self, name):
        """This method is called to process decimal and hexadecimal numeric character
        references of the form &#NNN; and &#xNNN;. For example, the decimal equivalent
        for &gt; is &#62;, whereas the hexadecimal is &#x3E;; in this case the method
        will receive '62' or 'x3E'.
        This method is never called if convert_charrefs is True."""

        self.elements.append(f"&#{name};")

    def handle_entityref(self, name):
        """This method is called to process a named character reference of
        the form &name; (e.g. &gt;), where name is a general entity reference (e.g. 'gt').
        This method is never called if convert_charrefs is True."""

        self.elements.append(f"&{name};")

    def handle_data(self, data):
        """This method is called to process arbitrary data (e.g. text nodes and
        the content of <script>...</script> and <style>...</style>)."""

        if self._enter_pre_tag:
            # adapt minihtml behavior for <pre> content
            data = _newline_to_br(_space_to_nbsp(data))

        self.elements.append(data)

    def handle_comment(self, data):
        """This method is called when a comment is encountered (e.g. <!--comment-->).

        For example, the comment <!-- comment --> will cause this method to be called
        with the argument ' comment '.

        The content of Internet Explorer conditional comments (condcoms) will also
        be sent to this method, so, for <!--[if IE 9]>IE9-specific content<![endif]-->,
        this method will receive '[if IE 9]>IE9-specific content<![endif]'."""

        self.elements.append(f"<!--{data}-->")

    def handle_decl(self, decl):
        """This method is called to handle an HTML doctype declaration (e.g. <!DOCTYPE html>).

        The decl parameter will be the entire contents of the declaration inside
        the <!...> markup (e.g. 'DOCTYPE html')."""

        self.elements.append(f"<!{decl}>")

    def handle_pi(self, data):
        """Method called when a processing instruction is encountered.
        The data parameter will contain the entire processing instruction.
        For example, for the processing instruction <?proc color='red'>,
        this method would be called as handle_pi("proc color='red'").
        It is intended to be overridden by a derived class; the base class
        implementation does nothing."""

        self.elements.append(f"<?{data}>")

    def unknown_decl(self, data):
        """This method is called when an unrecognized declaration is read by the parser.

        The data parameter will be the entire contents of the declaration inside the
        <![...]> markup. It is sometimes useful to be overridden by a derived class.
        The base class implementation does nothing."""

        self.elements.append(f"<![{data}]>")


def html_to_minihtml(html_text: str) -> MiniHTML:
    """convert html to minihtml implementation"""

    parser = MiniHTMLElementParser()
    parser.feed(html_text)
    return "".join(parser.elements)
