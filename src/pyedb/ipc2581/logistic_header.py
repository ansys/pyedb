# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
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

from pyedb.generic.general_methods import ET


class LogisticHeader(object):
    def __init__(self):
        self.owner = "PyEDB"
        self.sender = "Ansys"
        self.enterprise = "Ansys"
        self.code = "UNKNOWN"
        self.person_name = "eba"
        self.enterprise_ref = "UNKNOWN"
        self.role_ref = "PyEDB"

    def write_xml(self, root):  # pragma no cover
        logistic_header = ET.SubElement(root, "LogisticHeader")
        role = ET.SubElement(logistic_header, "Role")
        role.set("id", self.owner)
        role.set("roleFunction", self.sender)
        enterprise = ET.SubElement(logistic_header, "Enterprise")
        enterprise.set("id", self.enterprise)
        enterprise.set("code", self.code)
        person = ET.SubElement(logistic_header, "Person")
        person.set("name", self.person_name)
        person.set("enterpriseRef", self.enterprise_ref)
        person.set("roleRef", self.role_ref)
