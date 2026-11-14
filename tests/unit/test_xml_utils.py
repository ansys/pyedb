# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT

import pytest

from pyedb.xml_parser.xml_utils import dict_to_xml, parse_xml_to_dict

pytestmark = [pytest.mark.unit, pytest.mark.no_licence]


def test_parse_xml_bytes_with_repeated_children_and_mixed_text():
    xml = b'<Root id="sample"> before <Item>first</Item><Item>second</Item> after </Root>'

    assert parse_xml_to_dict(xml) == {
        "Root": {
            "@id": "sample",
            "Item": ["first", "second"],
            "#text": "before  after",
        }
    }


def test_dict_to_xml_handles_empty_values_booleans_and_mixed_content():
    xml = dict_to_xml(
        {
            "Root": {
                "@enabled": True,
                "@disabled": False,
                "empty": None,
                "blank": "",
                "text": {"#text": "A&B"},
                "mixed": {"@id": 1, "#text": "before <", "Child": "after &"},
            }
        },
        pretty=False,
    )

    assert xml == (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<Root enabled="true" disabled="false"><empty/><blank/><text>A&amp;B</text>'
        '<mixed id="1">before &lt;<Child>after &amp;</Child></mixed></Root>'
    )


@pytest.mark.parametrize(
    "data",
    [
        {"invalid name": "value"},
        {"Root": {"invalid name": "value"}},
        {"Root": {"@invalid name": "value"}},
    ],
)
def test_dict_to_xml_rejects_invalid_xml_names(data):
    with pytest.raises(ValueError, match="Invalid XML name"):
        dict_to_xml(data)


@pytest.mark.parametrize("data", [{}, {"Root": None, "Other": None}])
def test_dict_to_xml_requires_one_root(data):
    with pytest.raises(ValueError, match="exactly one root"):
        dict_to_xml(data)
