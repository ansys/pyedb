from pyedb.generic.constants import DCBehaviorMapper, SParamExtrapolationMapper,SparamInterpolationMapper


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
        self.core.Interpolation = getattr(self.core.Interpolation , temp)

    @property
    def use_state_space(self):
        return self.core.UseStateSpace

    @use_state_space.setter
    def use_state_space(self, value):
        self.core.UseStateSpace = value
