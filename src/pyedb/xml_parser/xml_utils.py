# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Minimal stdlib XML <-> dict conversion helpers.

The dictionary convention mirrors the one used by ``xmltodict``:

- attributes are stored with an ``@`` prefix,
- text of elements that also have attributes/children is stored under ``#text``,
- elements with only text are plain strings, empty elements are ``None``,
- repeated sibling tags become lists.

Namespace prefixes (for example ``c:Control``) are preserved verbatim.
"""

import re
from typing import Any
from xml.parsers import expat

import defusedxml

# Protect stdlib XML parsers against entity expansion and XXE attacks
defusedxml.defuse_stdlib()


def _escape_xml_text(text: str) -> str:
    """Escape XML special characters in text content.

    Parameters
    ----------
    text : str
        Text to escape.

    Returns
    -------
    str
        Text with XML special characters escaped.
    """
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    return text


def _quoteattr(value: str) -> str:
    """Quote and escape an XML attribute value.

    Parameters
    ----------
    value : str
        Attribute value to quote.

    Returns
    -------
    str
        Quoted and escaped attribute value.
    """
    value = value.replace("&", "&amp;")
    value = value.replace("<", "&lt;")
    value = value.replace(">", "&gt;")
    value = value.replace('"', "&quot;")
    return f'"{value}"'


# Aliases for backward compatibility with existing code patterns
escape = _escape_xml_text
quoteattr = _quoteattr

# XML name pattern: starts with letter/underscore/colon, followed by word chars/hyphens/underscores/colons/dots
# See: https://www.w3.org/TR/xml/#NT-Name
_XML_NAME_PATTERN = re.compile(r"^[a-zA-Z_:][a-zA-Z0-9_:.\-]*$")


def _validate_xml_name(name: str) -> None:
    """Validate that a string is a valid XML element or attribute name.

    Parameters
    ----------
    name : str
        The name to validate.

    Raises
    ------
    ValueError
        If the name is not a valid XML name.
    """
    if not name or not _XML_NAME_PATTERN.match(name):
        raise ValueError(
            f"Invalid XML name: {name!r}. Must start with letter, underscore, or colon, "
            f"and contain only alphanumeric characters, hyphens, underscores, dots, and colons."
        )


def parse_xml_to_dict(xml_string: str) -> dict:
    """Parse an XML string into a dictionary.

    Parameters
    ----------
    xml_string : str
        XML document content.

    Returns
    -------
    dict
        Dictionary with a single key (the root tag).
    """
    parser = expat.ParserCreate()  # no namespace processing: prefixes are kept as-is
    parser.buffer_text = True

    # Each stack item: [tag, attrs, children (list of (tag, value)), text chunks]
    stack: list = []
    result: dict = {}

    def start(tag, attrs):
        stack.append([tag, attrs, [], []])

    def chars(data):
        if stack:
            stack[-1][3].append(data)

    def end(tag):
        _, attrs, children, text_chunks = stack.pop()
        text = "".join(text_chunks).strip()
        if not attrs and not children:
            value: Any = text or None
        else:
            value = {f"@{k}": v for k, v in attrs.items()}
            for child_tag, child_value in children:
                if child_tag in value:
                    if not isinstance(value[child_tag], list):
                        value[child_tag] = [value[child_tag]]
                    value[child_tag].append(child_value)
                else:
                    value[child_tag] = child_value
            if text:
                value["#text"] = text
        if stack:
            stack[-1][2].append((tag, value))
        else:
            result[tag] = value

    parser.StartElementHandler = start
    parser.EndElementHandler = end
    parser.CharacterDataHandler = chars
    parser.Parse(xml_string.encode("utf-8") if isinstance(xml_string, str) else xml_string, True)
    return result


def _to_text(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _emit(tag: str, value: Any, level: int, pretty: bool, out: list) -> None:
    # Validate tag name to prevent XML injection
    _validate_xml_name(tag)

    if isinstance(value, list):
        for item in value:
            _emit(tag, item, level, pretty, out)
        return

    indent = "\t" * level if pretty else ""
    nl = "\n" if pretty else ""

    if not isinstance(value, dict):
        if value is None or value == "":
            out.append(f"{indent}<{tag}/>{nl}")
        else:
            out.append(f"{indent}<{tag}>{escape(_to_text(value))}</{tag}>{nl}")
        return

    # Validate attribute names and escape their values
    attrs = ""
    for k, v in value.items():
        if k.startswith("@") and v is not None:
            attr_name = k[1:]
            _validate_xml_name(attr_name)  # Validate attribute name
            attrs += f" {attr_name}={quoteattr(_to_text(v))}"

    text = value.get("#text")
    children = [(k, v) for k, v in value.items() if not k.startswith("@") and k != "#text"]

    if not children:
        if text is None or text == "":
            out.append(f"{indent}<{tag}{attrs}/>{nl}")
        else:
            out.append(f"{indent}<{tag}{attrs}>{escape(_to_text(text))}</{tag}>{nl}")
        return

    out.append(f"{indent}<{tag}{attrs}>{nl}")
    if text not in (None, ""):
        text_indent = indent + ("\t" if pretty else "")
        out.append(f"{text_indent}{escape(_to_text(text))}{nl}")
    for child_tag, child_value in children:
        _emit(child_tag, child_value, level + 1, pretty, out)
    out.append(f"{indent}</{tag}>{nl}")


def dict_to_xml(data: dict, pretty: bool = True) -> str:
    """Serialize a dictionary with a single root key into an XML string.

    Parameters
    ----------
    data : dict
        Dictionary with exactly one root key, using the ``@``/``#text`` convention.
    pretty : bool, optional
        Whether to indent the output with tabs. The default is ``True``.

    Returns
    -------
    str
        XML document, including the XML declaration.

    Raises
    ------
    ValueError
        If the data doesn't have exactly one root element or contains invalid XML names.
    """
    if len(data) != 1:
        raise ValueError("Document must have exactly one root element.")
    root_tag, root_value = next(iter(data.items()))
    _validate_xml_name(root_tag)  # Validate root tag name
    out: list = ['<?xml version="1.0" encoding="utf-8"?>' + ("\n" if pretty else "")]
    _emit(root_tag, root_value, 0, pretty, out)
    xml_str = "".join(out)
    return xml_str.rstrip("\n") if pretty else xml_str
