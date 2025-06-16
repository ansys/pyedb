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
# FITNE SS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from ansys.edb.core.utility.value import Value as GrpcValue


class SweepDataDistribution:
    @staticmethod
    def get_distribution(
        sweep_type="linear", start="0Ghz", stop="10GHz", step="10MHz", count=10, decade_number=6, octave_number=5
    ) -> str:
        """Return the Sweep data distribution.

        Parameters
        ----------
        sweep_type : str
            Sweep type. Supported values : `"linear"`, `"linear_count"`, `"exponential"`, `"decade_count"`,
            `"octave_count"`
        start : str, float
            Start frequency.
        stop : str, float
            Stop frequency
        step : str, float
            Step frequency
        count : int
            Count number
        decade_number : int
            Decade number
        octave_number : int
            Octave number

        Return
        ------
        str
            Sweep Data distribution.

        """
        if sweep_type.lower() == "linear":
            if isinstance(start, str) and isinstance(stop, str) and isinstance(step, str):
                return f"LIN {start} {stop} {step}"
            else:
                return f"LIN {GrpcValue(start).value} {GrpcValue(stop).value} {GrpcValue(step).value}"
        elif sweep_type.lower() == "linear_count":
            if isinstance(start, str) and isinstance(stop, str) and isinstance(count, int):
                return f"LINC {start} {stop} {count}"
            else:
                return f"LINC {GrpcValue(start).value} {GrpcValue(stop).value} {int(GrpcValue(count).value)}"
        elif sweep_type.lower() == "exponential":
            if isinstance(start, str) and isinstance(stop, str) and isinstance(count, int):
                return f"ESTP {start} {stop} {count}"
            else:
                return f"ESTP {GrpcValue(start).value} {GrpcValue(stop).value} {int(GrpcValue(count).value)}"
        elif sweep_type.lower() == "decade_count":
            if isinstance(start, str) and isinstance(stop, str) and isinstance(decade_number, int):
                return f"DEC {start} {stop} {decade_number}"
            else:
                return f"DEC {GrpcValue(start).value} {GrpcValue(stop).value} {int(GrpcValue(decade_number).value)}"
        elif sweep_type.lower() == "octave_count":
            if isinstance(start, str) and isinstance(stop, str) and isinstance(octave_number, int):
                return f"OCT {start} {stop} {octave_number}"
            else:
                return f"OCT {GrpcValue(start).value} {GrpcValue(stop).value} {int(GrpcValue(octave_number).value)}"
        else:
            return ""
