# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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

from pyedb.generic.constants import DCBehaviorMapper, SParamExtrapolationMapper, SparamInterpolationMapper


class SIwaveSParameterSettings:
    def __init__(self, parent, core):
        self._parent = parent
        self.core = core

    @property
    def dc_behavior(self):
        return DCBehaviorMapper.get(self.core.DCBehavior.ToString())

    @dc_behavior.setter
    def dc_behavior(self, value):
        temp = DCBehaviorMapper.get_dotnet(value)
        self.core.DCBehavior = getattr(self.core.DCBehavior, temp)

    @property
    def extrapolation(self):
        return SParamExtrapolationMapper.get(self.core.Extrapolation.ToString())

    @extrapolation.setter
    def extrapolation(self, value):
        temp = SParamExtrapolationMapper.get_dotnet(value)
        self.core.Extrapolation = getattr(self.core.Extrapolation, temp)

    @property
    def interpolation(self):
        return SparamInterpolationMapper.get(self.core.Interpolation.ToString())

    @interpolation.setter
    def interpolation(self, value):
        temp = SparamInterpolationMapper.get_dotnet(value)
        self.core.Interpolation = getattr(self.core.Interpolation, temp)

    @property
    def use_state_space(self):
        return self.core.UseStateSpace

    @use_state_space.setter
    def use_state_space(self, value):
        self.core.UseStateSpace = value
