# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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

import os.path
from pathlib import Path
import subprocess  # nosec B404

from pyedb.generic.general_methods import is_linux


class SiwaveSolve(object):
    def __init__(self, pedb):
        self._pedb = pedb

    @property
    def __siwave_exe_path(self):
        executable = "siwave"
        executable = executable if is_linux else executable + ".exe"
        full_path = Path(self._pedb.ansys_em_path) / executable
        return str(full_path)

    @property
    def __siwave_ng_exe_path(self):
        executable = "siwave_ng"
        executable = executable if is_linux else executable + ".exe"
        full_path = Path(self._pedb.ansys_em_path) / executable
        return str(full_path)

    def __create_exec(self, type):
        base = os.path.splitext(self._pedb.edbpath)[0]
        txt_path = base + ".txt"
        exec_path = base + ".exec"
        with open(txt_path, "w") as file:
            if type:
                if type == "DCIR":
                    file.write("ExecDcSim")
                elif type == "SYZ":
                    file.write("ExecSyzSim")
                elif type == "CPA":
                    file.write("ExecSentinelCpaSim")
                elif type == "TimeCrosstalk":
                    file.write("ExecTimeDomainCrosstalkSim")
                elif type == "FreqCrosstalk":
                    file.write("ExecCrosstalkSim")
                elif type == "Impedance":
                    file.write("ExecZ0Sim")

        os.rename(txt_path, exec_path)
        return exec_path

    def solve_siwave(self, edbpath, analysis_type):
        """Solve an SIWave setup. Only non-graphical batch mode is supported.

        .. warning::
            Do not execute this function with untrusted function argument, environment
            variables or pyedb global settings.
            See the :ref:`security guide<ref_security_consideration>` for details.

        Parameters
        ----------
        analysis_type: str
            Type of SIWave analysis to perform. Available types are "SYZ", "DCIR", "CPA", "TimeCrosstalk",
            "FreqCrosstalk", "Impedance".
        edbpath: str
            Full path to the .aedb folder, siw or siwz file to be solved.
        siwave_ng: str, optinial
            Path to the siwave_ng. Default is the SIWave installation path.
        """

        command = [
            self.__siwave_ng_exe_path,
            edbpath,
            self.__create_exec(type=analysis_type),
            "-formatOutput",
            "-useSubdir",
        ]
        try:
            subprocess.run(command, check=True)  # nosec
        except subprocess.CalledProcessError as e:  # nosec
            raise RuntimeError(f"An error occurred when launching the solver. Please check input paths") from e

    def solve(self, num_of_cores=4):
        """Solve using siwave_ng.exe

        .. warning::
            Do not execute this function with untrusted function argument, environment
            variables or pyedb global settings.
            See the :ref:`security guide<ref_security_consideration>` for details.

        """
        exec_file = os.path.splitext(self._pedb.edbpath)[0] + ".exec"
        if os.path.exists(exec_file):
            with open(exec_file, "r+") as f:
                content = f.readlines()
                if "SetNumCpus" not in content:
                    f.writelines(str.format("SetNumCpus {}", str(num_of_cores)) + "\n")
                    f.writelines("SaveSiw")
                else:
                    fstarts = [i for i in range(len(content)) if content[i].startswith("SetNumCpus")]
                    content[fstarts[0]] = str.format("SetNumCpus {}", str(num_of_cores))
                    f.close()
                    os.remove(exec_file)
                    f = open(exec_file, "w")
                    f.writelines(content)
        command = [self.__siwave_ng_exe_path, self._pedb.edbpath, exec_file, "-formatOutput -useSubdir"]
        try:
            subprocess.run(command, check=True)  # nosec
        except subprocess.CalledProcessError as e:  # nosec
            raise RuntimeError("An error occurred while solving") from e

    def export_3d_cad(
        self, format_3d="Q3D", output_folder=None, net_list=None, num_cores=4, aedt_file_name=None, hidden=False
    ):  # pragma: no cover
        """Export edb to Q3D or HFSS

        .. warning::
            Do not execute this function with untrusted function argument, environment
            variables or pyedb global settings.
            See the :ref:`security guide<ref_security_consideration>` for details.

        Parameters
        ----------
        format_3d : str, default ``Q3D``
        output_folder : str
            Output file folder. If `` then the aedb parent folder is used
        net_list : list, default ``None``
            Define Nets to Export. if None, all nets will be exported
        num_cores : int, optional
            Define number of cores to use during export
        aedt_file_name : str, optional
            Output  aedt file name (without .aedt extension). If `` then default naming is used
        Returns
        -------
        str
            path to aedt file
        """
        if not output_folder:
            output_folder = os.path.dirname(self._pedb.edbpath)
        scriptname = os.path.join(output_folder, "export_cad.py")
        with open(scriptname, "w") as f:
            f.write("import os\n")
            f.write("edbpath = r'{}'\n".format(self._pedb.edbpath))
            f.write("exportOptions = os.path.join(r'{}', 'options.config')\n".format(output_folder))
            f.write("oDoc.ScrImportEDB(edbpath)\n")
            f.write("oDoc.ScrSaveProjectAs(os.path.join(r'{}','{}'))\n".format(output_folder, "test.siw"))
            if net_list:
                f.write("allnets = []\n")
                for el in net_list:
                    f.write("allnets.append('{}')\n".format(el))
                f.write("for i in range(0, len(allnets)):\n")
                f.write("    if allnets[i] != 'DUMMY':\n")
                f.write("        oDoc.ScrSelectNet(allnets[i], 1)\n")
            f.write("oDoc.ScrSetOptionsFor3DModelExport(exportOptions)\n")
            if not aedt_file_name:
                aedt_file_name = format_3d + "_siwave.aedt"
            f.write("q3d_filename = os.path.join(r'{}', '{}')\n".format(output_folder, aedt_file_name))
            if num_cores:
                f.write("oDoc.ScrSetNumCpusToUse('{}')\n".format(num_cores))
            f.write("oDoc.ScrExport3DModel('{}', q3d_filename)\n".format(format_3d))
            f.write("oDoc.ScrCloseProject()\n")
            f.write("oApp.Quit()\n")

        command = [self.__siwave_exe_path]
        if hidden:
            command.append("-embedding")
        command += ["-RunScriptAndExit", scriptname]
        print(command)
        try:
            result = subprocess.run(command, check=True, capture_output=True)  # nosec
            print(result.stdout.decode())
        except subprocess.CalledProcessError as e:  # nosec
            raise RuntimeError("An error occurred while exporting 3D CAD") from e
        return os.path.join(output_folder, aedt_file_name)

    def export_dc_report(
        self,
        siwave_project,
        solution_name,
        output_folder=None,
        html_report=True,
        vias=True,
        voltage_probes=True,
        current_sources=True,
        voltage_sources=True,
        power_tree=True,
        loop_res=True,
        hidden=True,
    ):
        """Close EDB and solve it with Siwave.

        .. warning::
            Do not execute this function with untrusted function argument, environment
            variables or pyedb global settings.
            See the :ref:`security guide<ref_security_consideration>` for details.

        Parameters
        ----------
        siwave_project : str
            Siwave full project name.
        solution_name : str
            Siwave DC Analysis name.
        output_folder : str, optional
            Ouptu folder where files will be downloaded.
        html_report : bool, optional
            Either if generate or not html report. Default is `True`.
        vias : bool, optional
            Either if generate or not vias report. Default is `True`.
        voltage_probes : bool, optional
            Either if generate or not voltage probe report. Default is `True`.
        current_sources : bool, optional
            Either if generate or not current source report. Default is `True`.
        voltage_sources : bool, optional
            Either if generate or not voltage source report. Default is `True`.
        power_tree : bool, optional
            Either if generate or not power tree image. Default is `True`.
        loop_res : bool, optional
            Either if generate or not loop resistance report. Default is `True`.

        Returns
        -------
        list
            list of files generated.
        """
        if not output_folder:
            output_folder = os.path.dirname(self._pedb.edbpath)
        output_list = []
        scriptname = os.path.normpath(os.path.join(os.path.normpath(output_folder), "export_results.py"))
        with open(scriptname, "w") as f:
            f.write("oApp.OpenProject(r'{}')\n".format(siwave_project))
            if html_report:
                f.write("proj = oApp.GetActiveProject()\n")

                f.write("proj.ScrExportDcSimReportColorBarProperties(14,2,False,True)\n")

                f.write("proj.ScrExportDcSimReportScaling('All','All',-1,-1,False)\n")
                report_name = os.path.join(output_folder, solution_name + ".htm")
                f.write("proj.ScrExportDcSimReport('{}','White',r'{}')\n".format(solution_name, report_name))
                output_list.append(report_name)
            if vias:
                via_name = os.path.join(output_folder, "vias.txt")
                f.write("proj.ScrExportElementData('{}',r'{}','Vias')\n".format(solution_name, via_name))
                output_list.append(via_name)

            if voltage_probes:
                probes_names = os.path.join(output_folder, "voltage_probes.txt")
                f.write("proj.ScrExportElementData('{}',r'{}','Voltage Probes')\n".format(solution_name, probes_names))
                output_list.append(probes_names)

            if current_sources:
                source_name = os.path.join(output_folder, "current_sources.txt")

                f.write("proj.ScrExportElementData('{}',r'{}','Current Sources')\n".format(solution_name, source_name))
                output_list.append(source_name)

            if voltage_sources:
                sources = os.path.join(output_folder, "v_sources.txt")

                f.write("proj.ScrExportElementData('{}',r'{}','Voltage Sources')\n".format(solution_name, sources))
                output_list.append(sources)

            if power_tree:
                csv_file = os.path.join(output_folder, "powertree.csv")
                c = open(csv_file, "w")
                c.close()
                png_file = os.path.join(output_folder, "powertree.png")
                f.write("proj.ScrExportDcPowerTree('{}',r'{}', r'{}' )\n".format(solution_name, csv_file, png_file))
                output_list.append(png_file)

            if loop_res:
                f.write("sourceNames=[]\n")
                f.write("sourceData=[]\n")
                f.write("proj.ScrReadDCLoopResInfo('{}', sourceNames, sourceData)\n".format(solution_name))
                loop_res = os.path.join(output_folder, "loop_res.txt")
                f.write("with open(r'{}','w') as f:\n".format(loop_res))

                f.write("  f.writelines('Sources\tValue\\n')\n")

                f.write("  for a, b in zip(sourceNames, sourceData):\n")

                f.write("      f.writelines(a + '\t' + b + '\\n')\n")
                output_list.append(loop_res)

            f.write("proj.ScrCloseProject()\n")

            f.write("oApp.Quit()\n")
        command = [self.__siwave_exe_path]
        if hidden:
            command.append("-embedding")
        command.append("-RunScriptAndExit")
        command.append(scriptname)
        print(command)
        try:
            subprocess.run(command, check=True)  # nosec
        except subprocess.CalledProcessError as e:  # nosec
            raise RuntimeError("An error occurred while solving with Siwave") from e
        return output_list
