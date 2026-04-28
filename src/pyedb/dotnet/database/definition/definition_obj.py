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

from typing import Optional, Union
import warnings

from pydantic import BaseModel, confloat

from pyedb.dotnet.database.definition.dielectric_material_model import (
    DebyeModel,
    DjordjecvicSarkarModel,
    MultipoleDebyeModel,
)
from pyedb.dotnet.database.utilities.obj_base import ObjBase
from pyedb.misc.decorators import deprecated_property

try:
    from annotated_types import Gt
    from typing_extensions import Annotated

    PositiveFloat = Annotated[float, Gt(0)]
except:
    PositiveFloat = confloat(gt=0)

ATTRIBUTES = [
    "conductivity",
    "dielectric_loss_tangent",
    "magnetic_loss_tangent",
    "mass_density",
    "permittivity",
    "permeability",
    "poisson_ratio",
    "specific_heat",
    "thermal_conductivity",
    "youngs_modulus",
    "thermal_expansion_coefficient",
]
DC_ATTRIBUTES = [
    "dielectric_model_frequency",
    "loss_tangent_at_frequency",
    "permittivity_at_frequency",
    "dc_conductivity",
    "dc_permittivity",
]
PERMEABILITY_DEFAULT_VALUE = 1


class DefinitionObj(ObjBase):
    """Base class for definition objects."""

    def __init__(self, pedb, edb_object):
        super().__init__(pedb, edb_object)

    @property
    def definition_obj_type(self):
        return self._edb_object.GetDefinitionObjType()


class MaterialProperties(BaseModel):
    """Store material properties."""

    conductivity: Optional[PositiveFloat] = 0.0
    dielectric_loss_tangent: Optional[PositiveFloat] = 0.0
    magnetic_loss_tangent: Optional[PositiveFloat] = 0.0
    mass_density: Optional[PositiveFloat] = 0.0
    permittivity: Optional[PositiveFloat] = 0.0
    permeability: Optional[PositiveFloat] = 0.0
    poisson_ratio: Optional[PositiveFloat] = 0.0
    specific_heat: Optional[PositiveFloat] = 0.0
    thermal_conductivity: Optional[PositiveFloat] = 0.0
    youngs_modulus: Optional[PositiveFloat] = 0.0
    thermal_expansion_coefficient: Optional[PositiveFloat] = 0.0
    dc_conductivity: Optional[PositiveFloat] = 0.0
    dc_permittivity: Optional[PositiveFloat] = 0.0
    dielectric_model_frequency: Optional[PositiveFloat] = 0.0
    loss_tangent_at_frequency: Optional[PositiveFloat] = 0.0
    permittivity_at_frequency: Optional[PositiveFloat] = 0.0


class DeprecatedMaterial:
    """Manage EDB methods for material property management."""

    @property
    @deprecated_property("use dielectric_material_model property instead.", category=None)
    def dc_model(self):
        """Material dielectric model.

        .. deprecated:: 0.70.0
           Use ``dielectric_material_model`` instead.
        """
        warnings.warn(
            "`dc_model` is deprecated and will be removed in a future release. "
            "Use `dielectric_material_model` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.dielectric_material_model.core if self.dielectric_material_model else None

    @property
    def loss_tangent(self):
        """Get material loss tangent."""
        warnings.warn(
            "This method is deprecated in versions >0.7.0 and will soon be removed. "
            "Use property dielectric_loss_tangent instead.",
            DeprecationWarning,
        )
        return self.dielectric_loss_tangent

    @loss_tangent.setter
    def loss_tangent(self, value):
        """Set material loss tangent."""
        warnings.warn(
            "This method is deprecated in versions >0.7.0 and will soon be removed. "
            "Use property dielectric_loss_tangent instead.",
            DeprecationWarning,
        )
        self.dielectric_loss_tangent = value

    @property
    def dc_conductivity(self):
        """Get material dielectric conductivity."""
        res = None
        if self.dc_model:
            res = self.dc_model.GetDCConductivity()
        return res

    @dc_conductivity.setter
    def dc_conductivity(self, value: Union[int, float]):
        """Set material dielectric conductivity."""
        if self.dc_model and value:
            self.dc_model.SetDCConductivity(value)
        else:
            self.__edb.logger.error(f"DC conductivity cannot be updated in material without DC model or value {value}.")

    @property
    def dc_permittivity(self):
        """Get material dielectric relative permittivity"""
        res = None
        if self.dc_model:
            res = self.dc_model.GetDCRelativePermitivity()
        return res

    @dc_permittivity.setter
    def dc_permittivity(self, value: Union[int, float]):
        """Set material dielectric relative permittivity"""
        if self.dc_model and value:
            self.dc_model.SetDCRelativePermitivity(value)
        else:
            self.__edb.logger.error(f"DC permittivity cannot be updated in material without DC model or value {value}.")

    @property
    def dielectric_model_frequency(self):
        """Get material frequency in GHz."""
        res = None
        if self.dc_model:
            res = self.dc_model.GetFrequency()
        return res

    @dielectric_model_frequency.setter
    def dielectric_model_frequency(self, value: Union[int, float]):
        """Get material frequency in GHz."""
        if self.dc_model:
            self.dc_model.SetFrequency(value)
        else:
            self.__edb.logger.error(f"Material frequency cannot be updated in material without DC model.")

    @property
    def loss_tangent_at_frequency(self):
        """Get material loss tangeat at frequency."""
        res = None
        if self.dc_model:
            res = self.dc_model.GetLossTangentAtFrequency()
        return res

    @loss_tangent_at_frequency.setter
    def loss_tangent_at_frequency(self, value):
        """Set material loss tangent at frequency."""
        if self.dc_model:
            edb_value = self._pedb.value(value)
            self.dc_model.SetLossTangentAtFrequency(edb_value.core)
        else:
            self.__edb.logger.error(f"Loss tangent at frequency cannot be updated in material without DC model.")

    @property
    def permittivity_at_frequency(self):
        """Get material relative permittivity at frequency."""
        res = None
        if self.dc_model:
            res = self.dc_model.GetRelativePermitivityAtFrequency()
        return res

    @permittivity_at_frequency.setter
    def permittivity_at_frequency(self, value: Union[int, float]):
        """Set material relative permittivity at frequency."""
        if self.dc_model:
            self.dc_model.SetRelativePermitivityAtFrequency(value)
        else:
            self.__edb.logger.error(f"Permittivity at frequency cannot be updated in material without DC model.")

    def to_dict(self):
        """Convert material into dictionary."""
        properties = self.__load_all_properties()

        res = {"name": self.name}
        res.update(properties.model_dump())
        return res

    def update(self, input_dict: dict):
        if input_dict:
            # Update attributes
            for attribute in ATTRIBUTES:
                if attribute in input_dict:
                    setattr(self, attribute, input_dict[attribute])
            if "loss_tangent" in input_dict:  # pragma: no cover
                setattr(self, "loss_tangent", input_dict["loss_tangent"])

            # Update DS model
            # NOTE: Contrary to before we don't test 'dielectric_model_frequency' only
            if any(map(lambda attribute: input_dict.get(attribute, None) is not None, DC_ATTRIBUTES)):
                if not self.dc_model:
                    self.set_djordjecvic_sarkar_model()
                for attribute in DC_ATTRIBUTES:
                    if attribute in input_dict:
                        if attribute == "dc_permittivity" and input_dict[attribute] is not None:
                            self.dc_model.SetUseDCRelativePermitivity(True)
                        setattr(self, attribute, input_dict[attribute])
                self.core.SetDielectricMaterialModel(self.dc_model)
            # Unset DS model if it is already assigned to the material in the database
            elif self.dc_model:
                self.core.SetDielectricMaterialModel(self._pedb.value(None))

    def __load_all_properties(self) -> MaterialProperties:
        """Load all properties of the material."""
        res = MaterialProperties()
        for property in res.model_dump().keys():
            value = getattr(self, property)
            setattr(res, property, value)
        return res

    def set_thermal_modifier(
        self,
        property_name: str,
        basic_quadratic_temperature_reference: float = 21,
        basic_quadratic_c1: float = 0.1,
        basic_quadratic_c2: float = 0.1,
        advanced_quadratic_lower_limit: float = -270,
        advanced_quadratic_upper_limit: float = 1001,
        advanced_quadratic_auto_calculate: bool = False,
        advanced_quadratic_lower_constant: float = 1.1,
        advanced_quadratic_upper_constant: float = 1.1,
    ):
        """Sets the material property thermal modifier of a given material property.

        Parameters
        ----------
        property_name : str
            Name of the property to modify.
        basic_quadratic_temperature_reference : float, optional
            The TempRef value in the quadratic model.
        basic_quadratic_c1 : float, optional
            The C1 value in the quadratic model.
        basic_quadratic_c2 : float, optional
            The C2 value in the quadratic model.
        advanced_quadratic_lower_limit : float, optional
            The lower temperature limit where the quadratic model is valid.
        advanced_quadratic_upper_limit : float, optional
            The upper temperature limit where the quadratic model is valid.
        advanced_quadratic_auto_calculate : bool, optional
             The flag indicating whether or the LowerConstantThermalModifierVal and UpperConstantThermalModifierVal
             values should be auto calculated.
        advanced_quadratic_lower_constant : float, optional
            The constant thermal modifier value for temperatures lower than LowerConstantThermalModifierVal.
        advanced_quadratic_upper_constant : float, optional
            The constant thermal modifier value for temperatures greater than UpperConstantThermalModifierVal.

        Returns
        -------

        """
        _edb = self._pedb._edb
        basic = _edb.Utility.BasicQuadraticParams(
            _edb.Utility.Value(basic_quadratic_temperature_reference),
            _edb.Utility.Value(basic_quadratic_c1),
            _edb.Utility.Value(basic_quadratic_c2),
        )
        advanced = _edb.Utility.AdvancedQuadraticParams(
            _edb.Utility.Value(advanced_quadratic_lower_limit),
            _edb.Utility.Value(advanced_quadratic_upper_limit),
            advanced_quadratic_auto_calculate,
            _edb.Utility.Value(advanced_quadratic_lower_constant),
            _edb.Utility.Value(advanced_quadratic_upper_constant),
        )

        thermal_modifier = _edb.Definition.MaterialPropertyThermalModifier(basic, advanced)
        if not self.core.SetThermalModifier(self.material_property_id_mapping[property_name], thermal_modifier):
            raise ValueError(f"Fail to set thermal modifier for property {property_name}")
        else:
            return True


class MaterialDef(DefinitionObj, DeprecatedMaterial):
    """Class for material definition."""

    def __init__(self, edb, material_def):
        super().__init__(edb, material_def)
        self.property_id = self._pedb.core.Definition.MaterialPropertyId
        self.material_property_id_mapping = {
            "conductivity": self.property_id.Conductivity,
            "permittivity": self.property_id.Permittivity,
            "dielectric_loss_tangent": self.property_id.DielectricLossTangent,
            "magnetic_loss_tangent": self.property_id.MagneticLossTangent,
            "mass_density": self.property_id.MassDensity,
            "permeability": self.property_id.Permeability,
            "poisson_ratio": self.property_id.PoissonsRatio,
            "specific_heat": self.property_id.SpecificHeat,
            "thermal_conductivity": self.property_id.ThermalConductivity,
            "thermal_expansion_coefficient": self.property_id.ThermalExpansionCoefficient,
        }

    @classmethod
    def create(cls, pedb, name: str) -> "MaterialDef":
        """Creates a material definition into the database with given name."""
        edb_object = pedb._edb.Definition.MaterialDef.Create(pedb.active_db, name)
        return cls(pedb, edb_object)

    @property
    def dielectric_material_model(self):
        """dielectric material model. Set None to remove the existing model."""
        e_obj = self._edb_object.GetDielectricMaterialModel()
        if e_obj is None:
            return None
        elif e_obj.GetType().get_FullName().endswith("DjordjecvicSarkarModel"):
            return DjordjecvicSarkarModel(self._pedb, e_obj)
        else:
            raise

    @dielectric_material_model.setter
    def dielectric_material_model(self, model: DjordjecvicSarkarModel | DebyeModel | MultipoleDebyeModel | None):
        if model:
            self._edb_object.SetDielectricMaterialModel(model._edb_object)
        else:
            self._edb_object.SetDielectricMaterialModel(None)

    def set_djordjecvic_sarkar_model(
        self,
        dc_conductivity: float | None = 1e-12,
        dc_relative_permittivity: float | None = 5,
        frequency: float | None = 1e9,
        loss_tangent_at_frequency: float | None = 0.02,
        relative_permittivity_at_frequency: float | None = 4,
        use_dc_relative_permittivity: bool | None = False,
    ) -> DjordjecvicSarkarModel:
        """Sets the dielectric material model to Djordjecvic-Sarkar model. The returned model is read-only, any change
        on it will not be reflected on the database.

        Parameters
        ----------
        dc_conductivity : float, optional
            DC conductivity, by default 1e-12
        dc_relative_permittivity : float, optional
            DC relative permittivity, by default 5
        frequency : float, optional
            Frequency in Hz, by default 1e9
        loss_tangent_at_frequency : float, optional
            Loss tangent at frequency, by default 0.02
        relative_permittivity_at_frequency : float, optional
            Relative permittivity at frequency, by default 4
        use_dc_relative_permittivity : bool, optional
            Whether to use DC relative permittivity, by default False

        """
        ds_model = DjordjecvicSarkarModel.create(self._pedb)
        ds_model.dc_conductivity = dc_conductivity
        ds_model.dc_relative_permittivity = dc_relative_permittivity
        ds_model.frequency = frequency
        ds_model.loss_tangent_at_frequency = loss_tangent_at_frequency
        ds_model.relative_permittivity_at_frequency = relative_permittivity_at_frequency
        ds_model.use_dc_relative_permittivity = use_dc_relative_permittivity
        self.dielectric_material_model = ds_model
        return ds_model

    @property
    def conductivity(self):
        """Get material conductivity."""
        material_property_id = self.property_id.Conductivity
        _, val = self.core.GetProperty(material_property_id)
        return val

    @conductivity.setter
    def conductivity(self, value):
        """Set material conductivity."""
        edb_value = self._pedb.value(value)
        material_property_id = self.property_id.Conductivity
        self.core.SetProperty(material_property_id, edb_value.core)

    @property
    def permittivity(self):
        """Get material permittivity."""
        material_property_id = self.property_id.Permittivity
        _, val = self.core.GetProperty(material_property_id)
        return val

    @permittivity.setter
    def permittivity(self, value):
        """Set material permittivity."""
        edb_value = self._pedb.value(value)
        material_property_id = self.property_id.Permittivity
        self.core.SetProperty(material_property_id, edb_value.core)

    @property
    def permeability(self):
        """Get material permeability."""
        material_property_id = self.property_id.Permeability
        _, val = self.core.GetProperty(material_property_id)
        return val

    @permeability.setter
    def permeability(self, value):
        """Set material permeability."""
        edb_value = self._pedb.value(value)
        material_property_id = self.property_id.Permeability
        self.core.SetProperty(material_property_id, edb_value.core)

    @property
    def dielectric_loss_tangent(self):
        """Get material loss tangent."""
        material_property_id = self.property_id.DielectricLossTangent
        _, val = self.core.GetProperty(material_property_id)
        return val

    @dielectric_loss_tangent.setter
    def dielectric_loss_tangent(self, value):
        edb_value = self._pedb.value(value)
        material_property_id = self.property_id.DielectricLossTangent
        self.core.SetProperty(material_property_id, edb_value.core)

    @property
    def magnetic_loss_tangent(self):
        """Get material magnetic loss tangent."""
        material_property_id = self.property_id.MagneticLossTangent
        _, val = self.core.GetProperty(material_property_id)
        return val

    @magnetic_loss_tangent.setter
    def magnetic_loss_tangent(self, value):
        """Set material magnetic loss tangent."""
        edb_value = self._pedb.value(value)
        material_property_id = self.property_id.MagneticLossTangent
        self.core.SetProperty(material_property_id, edb_value.core)

    @property
    def thermal_conductivity(self):
        """Get material thermal conductivity."""
        material_property_id = self.property_id.ThermalConductivity
        _, val = self.core.GetProperty(material_property_id)
        return val

    @thermal_conductivity.setter
    def thermal_conductivity(self, value):
        """Set material thermal conductivity."""
        edb_value = self._pedb.value(value)
        material_property_id = self.property_id.ThermalConductivity
        self.core.SetProperty(material_property_id, edb_value.core)

    @property
    def mass_density(self):
        """Get material mass density."""
        material_property_id = self.property_id.MassDensity
        _, val = self.core.GetProperty(material_property_id)
        return val

    @mass_density.setter
    def mass_density(self, value):
        """Set material mass density."""
        edb_value = self._pedb.value(value)
        material_property_id = self.property_id.MassDensity
        self.core.SetProperty(material_property_id, edb_value.core)

    @property
    def youngs_modulus(self):
        """Get material youngs modulus."""
        material_property_id = self.property_id.YoungsModulus
        _, val = self.core.GetProperty(material_property_id)
        return val

    @youngs_modulus.setter
    def youngs_modulus(self, value):
        """Set material youngs modulus."""
        edb_value = self._pedb.value(value)
        material_property_id = self.property_id.YoungsModulus
        self.core.SetProperty(material_property_id, edb_value.core)

    @property
    def specific_heat(self):
        """Get material specific heat."""
        material_property_id = self.property_id.SpecificHeat
        _, val = self.core.GetProperty(material_property_id)
        return val

    @specific_heat.setter
    def specific_heat(self, value):
        """Set material specific heat."""
        edb_value = self._pedb.value(value)
        material_property_id = self.property_id.SpecificHeat
        self.core.SetProperty(material_property_id, edb_value.core)

    @property
    def poisson_ratio(self):
        """Get material poisson ratio."""
        material_property_id = self.property_id.PoissonsRatio
        _, val = self.core.GetProperty(material_property_id)
        return val

    @poisson_ratio.setter
    def poisson_ratio(self, value):
        """Set material poisson ratio."""
        edb_value = self._pedb.value(value)
        material_property_id = self.property_id.PoissonsRatio
        self.core.SetProperty(material_property_id, edb_value.core)

    @property
    def thermal_expansion_coefficient(self):
        """Get material thermal coefficient."""
        material_property_id = self.property_id.ThermalExpansionCoefficient
        _, val = self.core.GetProperty(material_property_id)
        return val

    @thermal_expansion_coefficient.setter
    def thermal_expansion_coefficient(self, value):
        """Set material thermal coefficient."""
        edb_value = self._pedb.value(value)
        material_property_id = self.property_id.ThermalExpansionCoefficient
        self.core.SetProperty(material_property_id, edb_value.core)
