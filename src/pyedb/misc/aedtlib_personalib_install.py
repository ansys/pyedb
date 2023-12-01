from xml.dom.minidom import parseString
import xml.etree.ElementTree as ET


def write_pretty_xml(root, file_path):
    """Write the XML in a pretty format."""
    # If we use the commented code below, then the previously existing lines will have double lines added. We need to
    # split and ignore the double lines.
    # xml_str = parseString(ET.tostring(root)).toprettyxml(indent=" " * 4)
    lines = [line for line in parseString(ET.tostring(root)).toprettyxml(indent=" " * 4).split("\n") if line.strip()]
    xml_str = "\n".join(lines)

    with open(file_path, "w") as f:
        f.write(xml_str)
