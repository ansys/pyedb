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

from datetime import date

from pyedb.generic.general_methods import ET


class HistoryRecord(object):
    def __init__(self):
        self.number = "1"
        self.origination = date.today()
        self.software = "Ansys PyEDB"
        self.last_changes = date.today()
        self.file_revision = "1"
        self.comment = ""
        self.software_package = "Ansys AEDT"
        self.revision = "R2023.1"
        self.vendor = "Ansys"
        self.certification_status = "CERTIFIED"

    def write_xml(self, root):  # pragma no cover
        history_record = ET.SubElement(root, "HistoryRecord")
        history_record.set("number", self.number)
        history_record.set(
            "origination", "{}_{}_{}".format(self.origination.day, self.origination.month, self.origination.year)
        )
        history_record.set("software", self.software)
        history_record.set(
            "lastChange", "{}_{}_{}".format(self.origination.day, self.origination.month, self.origination.year)
        )
        file_revision = ET.SubElement(history_record, "FileRevision")
        file_revision.set("fileRevisionId", self.file_revision)
        file_revision.set("comment", self.comment)
        software_package = ET.SubElement(file_revision, "SoftwarePackage")
        software_package.set("name", self.software_package)
        software_package.set("revision", self.revision)
        software_package.set("vendor", self.vendor)
        certification = ET.SubElement(software_package, "Certification")
        certification.set("certificationStatus", self.certification_status)
