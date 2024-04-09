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

from __future__ import absolute_import  # noreorder

import difflib
import logging
import os
import re

from pydantic import BaseModel

from pyedb import Edb
from pyedb.dotnet.clr_module import _clr
from pyedb.dotnet.edb_core.general import convert_py_list_to_net_list
from pyedb.exceptions import MaterialModelException
from pyedb.generic.general_methods import is_ironpython, pyedb_function_handler

logger = logging.getLogger(__name__)

from typing import Optional, Union

from pydantic import BaseModel, confloat

# TODO: Once we are Python3.9+ change PositiveInt implementation like
# from annotated_types import Gt
# from typing_extensions import Annotated
# PositiveFloat = Annotated[float, Gt(0)]
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
DC_ATTRIBUTES =  [
    "dielectric_model_frequency",
    "loss_tangent_at_frequency",
    "permittivity_at_frequency",
    "dc_conductivity",
    "dc_permittivity",
]

class MaterialProperties(BaseModel):
    """Store material properties."""

    conductivity: Optional[PositiveFloat] = None
    dielectric_loss_tangent: Optional[PositiveFloat] = None
    magnetic_loss_tangent: Optional[PositiveFloat] = None
    mass_density: Optional[PositiveFloat] = None
    permittivity: Optional[PositiveFloat] = None
    permeability: Optional[PositiveFloat] = None
    poisson_ratio: Optional[PositiveFloat] = None
    specific_heat: Optional[PositiveFloat] = None
    thermal_conductivity: Optional[PositiveFloat] = None
    youngs_modulus: Optional[PositiveFloat] = None
    thermal_expansion_coefficient: Optional[PositiveFloat] = None
    dc_conductivity: Optional[PositiveFloat] = None
    dc_permittivity: Optional[PositiveFloat] = None
    dielectric_model_frequency: Optional[PositiveFloat] = None
    loss_tangent_at_frequency: Optional[PositiveFloat] = None
    permittivity_at_frequency: Optional[PositiveFloat] = None


class Material(object):
    """Manage EDB methods for material property management."""

    def __init__(self, edb: Edb, material_def):
        self.__edb: Edb = edb
        self.__edb_definition = edb.edb_api.definition
        self.__name: str = material_def.GetName()
        self.__material_def = material_def
        self.__dc_model = material_def.GetDielectricMaterialModel()
        self.__properties: MaterialProperties = MaterialProperties()

    @property
    def name(self):
        """Material name."""
        return self.__name

    @property
    def dc_model(self):
        """Material dielectric model."""
        return self.__dc_model

    @property
    def conductivity(self):
        """Get material conductivity."""
        if self.__properties.conductivity is None:
            material_property_id = self.__edb_definition.MaterialPropertyId.Conductivity
            self.__properties.conductivity = self.__property_value(material_property_id)
        return self.__properties.conductivity

    @conductivity.setter
    def conductivity(self, value):
        """Set material conductivity."""
        edb_value = self.__edb_value(value)
        material_property_id = self.__edb_definition.MaterialPropertyId.Conductivity
        self.__material_def.SetProperty(material_property_id, self.__edb_value(value))
        self.__properties.conductivity = edb_value.ToDouble()

    @property
    def permittivity(self):
        """Get material permittivity."""
        if self.__properties.permittivity is None:
            material_property_id = self.__edb_definition.MaterialPropertyId.Permittivity
            self.__properties.permittivity = self.__property_value(material_property_id)
        return self.__properties.permittivity

    @permittivity.setter
    def permittivity(self, value):
        """Set material permittivity."""
        edb_value = self.__edb_value(value)
        material_property_id = self.__edb_definition.MaterialPropertyId.Permittivity
        self.__material_def.SetProperty(material_property_id, edb_value)
        self.__properties.permittivity = edb_value.ToDouble()

    @property
    def permeability(self):
        """Get material permeability."""
        if self.__properties.permeability is None:
            material_property_id = self.__edb_definition.MaterialPropertyId.Permeability
            self.__properties.permeability = self.__property_value(material_property_id)
        return self.__properties.permeability

    @permeability.setter
    def permeability(self, value):
        """Set material permeability."""
        edb_value = self.__edb_value(value)
        material_property_id = self.__edb_definition.MaterialPropertyId.Permeability
        self.__material_def.SetProperty(material_property_id, edb_value)
        self.__properties.permeability = edb_value.ToDouble()

    @property
    def dielectric_loss_tangent(self):
        """Get material loss tangent."""
        if self.__properties.dielectric_loss_tangent is None:
            material_property_id = self.__edb_definition.MaterialPropertyId.DielectricLossTangent
            self.__properties.dielectric_loss_tangent = self.__property_value(material_property_id)
        return self.__properties.dielectric_loss_tangent

    @dielectric_loss_tangent.setter
    def dielectric_loss_tangent(self, value):
        """Set material loss tangent."""
        edb_value = self.__edb_value(value)
        material_property_id = self.__edb_definition.MaterialPropertyId.DielectricLossTangent
        self.__material_def.SetProperty(material_property_id, edb_value)
        self.__properties.dielectric_loss_tangent = edb_value.ToDouble()

    @property
    def dc_conductivity(self):
        """Get material dielectric conductivity."""
        if self.__dc_model and self.__properties.dc_conductivity is None:
            self.__properties.dc_conductivity = self.__dc_model.GetDCConductivity()
        return self.__properties.dc_conductivity

    @dc_conductivity.setter
    def dc_conductivity(self, value: Union[int, float]):
        """Set material dielectric conductivity."""
        if self.__dc_model:
            self.__dc_model.SetDCConductivity(value)
            self.__properties.dc_conductivity = value

    @property
    def dc_permittivity(self):
        """Get material dielectric relative permittivity"""
        if self.__dc_model and self.__properties.dc_permittivity is None:
            self.__properties.dc_permittivity = self.__dc_model.GetDCRelativePermitivity()
        return self.__properties.dc_permittivity

    @dc_permittivity.setter
    def dc_permittivity(self, value: Union[int, float]):
        """Set material dielectric relative permittivity"""
        if self.__dc_model:
            self.__dc_model.SetDCRelativePermitivity(value)
            self.__properties.dc_permittivity = value

    @property
    def dielectric_model_frequency(self):
        """Get material frequency in GHz."""
        if self.__dc_model and self.__properties.dielectric_model_frequency is None:
            self.__properties.dielectric_model_frequency = self.__dc_model.GetFrequency()
        return self.__properties.dielectric_model_frequency

    @dielectric_model_frequency.setter
    def dielectric_model_frequency(self, value: Union[int, float]):
        """Get material frequency in GHz."""
        if self.__dc_model:
            self.__dc_model.SetFrequency(value)
            self.__properties.dielectric_model_frequency = value

    @property
    def loss_tangent_at_frequency(self):
        """Get material loss tangeat at frequency."""
        if self.__dc_model and self.__properties.loss_tangent_at_frequency is None:
            self.__properties.loss_tangent_at_frequency = self.__dc_model.GetLossTangentAtFrequency()
        return self.__properties.loss_tangent_at_frequency

    @loss_tangent_at_frequency.setter
    def loss_tangent_at_frequency(self, value):
        """Set material loss tangeat at frequency."""
        if self.__dc_model:
            edb_value = self.__edb_value(value)
            self.__dc_model.SetLossTangentAtFrequency(edb_value)
            self.__properties.dielectric_model_frequency = edb_value.ToDouble()

    @property
    def permittivity_at_frequency(self):
        """Get material relative permittivity at frequency."""
        if self.__dc_model and self.__properties.permittivity_at_frequency is None:
            self.__properties.permittivity_at_frequency = self.__dc_model.GetRelativePermitivityAtFrequency()
        return self.__properties.permittivity_at_frequency

    @permittivity_at_frequency.setter
    def permittivity_at_frequency(self, value: Union[int, float]):
        """Set material relative permittivity at frequency."""
        if self.__dc_model:
            self.__dc_model.SetRelativePermitivityAtFrequency(value)
            self.__properties.permittivity_at_frequency = value

    @property
    def magnetic_loss_tangent(self):
        """Get material magnetic loss tangent."""
        if self.__properties.magnetic_loss_tangent is None:
            material_property_id = self.__edb_definition.MaterialPropertyId.MagneticLossTangent
            self.__properties.magnetic_loss_tangent = self.__property_value(material_property_id)
        return self.__properties.magnetic_loss_tangent

    @magnetic_loss_tangent.setter
    def magnetic_loss_tangent(self, value):
        """Set material magnetic loss tangent."""
        edb_value = self.__edb_value(value)
        material_property_id = self.__edb_definition.MaterialPropertyId.MagneticLossTangent
        self.__material_def.SetProperty(material_property_id, edb_value)
        self.__properties.magnetic_loss_tangent = edb_value.ToDouble()

    @property
    def thermal_conductivity(self):
        """Get material thermal conductivity."""
        if self.__properties.thermal_conductivity is None:
            material_property_id = self.__edb_definition.MaterialPropertyId.ThermalConductivity
            self.__properties.thermal_conductivity = self.__property_value(material_property_id)
        return self.__properties.thermal_conductivity

    @thermal_conductivity.setter
    def thermal_conductivity(self, value):
        """Set material thermal conductivity."""
        edb_value = self.__edb_value(value)
        material_property_id = self.__edb_definition.MaterialPropertyId.ThermalConductivity
        self.__material_def.SetProperty(material_property_id, edb_value)
        self.__properties.thermal_conductivity = edb_value.ToDouble()

    @property
    def mass_density(self):
        """Get material mass density."""
        if self.__properties.thermal_conductivity is None:
            material_property_id = self.__edb_definition.MaterialPropertyId.MassDensity
            self.__properties.mass_density = self.__property_value(material_property_id)
        return self.__properties.mass_density

    @mass_density.setter
    def mass_density(self, value):
        """Set material mass density."""
        edb_value = self.__edb_value(value)
        material_property_id = self.__edb_definition.MaterialPropertyId.MassDensity
        self.__material_def.SetProperty(material_property_id, edb_value)
        self.__properties.mass_density = edb_value.ToDouble()

    @property
    def youngs_modulus(self):
        """Get material youngs modulus."""
        if self.__properties.youngs_modulus is None:
            material_property_id = self.__edb_definition.MaterialPropertyId.YoungsModulus
            self.__properties.youngs_modulus = self.__property_value(material_property_id)
        return self.__properties.youngs_modulus

    @youngs_modulus.setter
    def youngs_modulus(self, value):
        """Set material youngs modulus."""
        edb_value = self.__edb_value(value)
        material_property_id = self.__edb_definition.MaterialPropertyId.YoungsModulus
        self.__material_def.SetProperty(material_property_id, edb_value)
        self.__properties.youngs_modulus = edb_value.ToDouble()

    @property
    def specific_heat(self):
        """Get material specific heat."""
        if self.__properties.specific_heat is None:
            material_property_id = self.__edb_definition.MaterialPropertyId.SpecificHeat
            self.__properties.specific_heat = self.__property_value(material_property_id)
        return self.__properties.specific_heat

    @specific_heat.setter
    def specific_heat(self, value):
        """Set material specific heat."""
        edb_value = self.__edb_value(value)
        material_property_id = self.__edb_definition.MaterialPropertyId.SpecificHeat
        self.__material_def.SetProperty(material_property_id, edb_value)
        self.__properties.specific_heat = edb_value.ToDouble()

    @property
    def poisson_ratio(self):
        """Get material poisson ratio."""
        if self.__properties.specific_heat is None:
            material_property_id = self.__edb_definition.MaterialPropertyId.PoissonsRatio
            self.__properties.poisson_ratio = self.__property_value(material_property_id)
        return self.__properties.poisson_ratio

    @poisson_ratio.setter
    def poisson_ratio(self, value):
        """Set material poisson ratio."""
        edb_value = self.__edb_value(value)
        material_property_id = self.__edb_definition.MaterialPropertyId.PoissonsRatio
        self.__material_def.SetProperty(material_property_id, edb_value)
        self.__properties.poisson_ratio = edb_value.ToDouble()

    @property
    def thermal_expansion_coefficient(self):
        """Get material thermal coefficient."""
        if self.__properties.thermal_expansion_coefficient is None:
            material_property_id = self.__edb_definition.MaterialPropertyId.ThermalExpansionCoefficient
            self.__properties.thermal_expansion_coefficient = self.__property_value(material_property_id)
        return self.__properties.thermal_expansion_coefficient

    @thermal_expansion_coefficient.setter
    def thermal_expansion_coefficient(self, value):
        """Set material thermal coefficient."""
        edb_value = self.__edb_value(value)
        material_property_id = self.__edb_definition.MaterialPropertyId.ThermalExpansionCoefficient
        self.__material_def.SetProperty(material_property_id, self.__edb_value(value))
        self.__properties.thermal_expansion_coefficient = edb_value.ToDouble()

    @pyedb_function_handler()
    def to_dict(self):
        """Convert material into dictionnary."""
        self.__load_all_properties()

        res = {"name": self.name}
        res.update(self.__properties.model_dump())
        return res

    @pyedb_function_handler()
    def update(self, input_dict: dict):
        if input_dict:
            # Update attributes
            for attribute in ATTRIBUTES:
                if attribute in input_dict:
                    setattr(self, attribute, input_dict[attribute])

            # Update DS model
            # NOTE: Contrary to before we don't test 'dielectric_model_frequency' only
            if any(map(lambda attribute: input_dict.get(attribute, None) is not None, DC_ATTRIBUTES)):
                if not self.__dc_model:
                    self.__dc_model = self.__edb_definition.DjordjecvicSarkarModel()
                for attribute in DC_ATTRIBUTES:
                    if attribute in input_dict:
                        if attribute == "dc_permittivity" and input_dict[attribute] is not None:
                            self.__dc_model.SetUseDCRelativePermitivity(True)
                        setattr(self, attribute, input_dict[attribute])
            # Unset DS model if it is already assigned to the material in the database
            elif self.__dc_model:
                self.__material_def.SetDielectricMaterialModel(self.__edb_value(None))

    @pyedb_function_handler()
    def __edb_value(self, value):
        """Convert a value to an EDB value.

        Parameters
        ----------
        val : str, float, int
        """
        return self.__edb.edb_value(value)

    @pyedb_function_handler()
    def __load_all_properties(self):
        """Load all properties of the material."""
        for property in self.__properties.model_dump().keys():
            _ = getattr(self, property)

    @pyedb_function_handler()
    def __property_value(self, material_property_id):
        """Get property value from a material property id."""
        if is_ironpython:  # pragma: no cover
            property_box = _clr.StrongBox[float]()
            self.__material_def.GetProperty(material_property_id, property_box)
            return float(property_box)
        else:
            _, property_box = self.__material_def.GetProperty(material_property_id)
            if isinstance(property_box, float):
                return property_box
            else:
                return property_box.ToDouble()

    # def __reset_property(self, name):
    #     """Reset a property using the default value of the EDB API.
    #
    #     This method consists in reseting the value of a property by updating the inner property
    #     to ``None`` and accessing the property afterward. When one wants to access a property
    #     whose stored inner value is ``None``, the value is updated to the EDB API default value
    #     associated to that property.
    #     """
    #     # Update inner property to None
    #     setattr(self.__properties, name, None)
    #     # Trigger get value on the property
    #     _ = getattr(self, name)


class Materials(object):
    """Manages EDB methods for material management accessible from `Edb.materials` property."""

    def __init__(self, edb: Edb):
        self.__edb = edb
        self.__edb_definition = edb.edb_api.definition
        self.__syslib = os.path.join(self.__edb.base_path, "syslib")
        self.__materials: dict[str, Material] = {
            material_def.GetName(): Material(self.__edb, material_def)
            for material_def in list(self.__edb.active_db.MaterialDefs)
        }

    def __contains__(self, item):
        if isinstance(item, Material):
            return item.name in self.__materials
        else:
            return item in self.__materials

    def __getitem__(self, item):
        return self.__materials[item]

    @property
    def syslib(self):
        """Get the project sys library."""
        return self.__syslib

    @property
    def materials(self):
        """Get materials."""
        return self.__materials

    def __edb_value(self, value):
        """Convert a value to an EDB value.

        Parameters
        ----------
        val : str, float, int
        """
        return self.__edb.edb_value(value)

    @pyedb_function_handler()
    def add_material(self, name: str, **kwargs):
        """Add a new material.

        Parameters
        ----------
        name : str
            Material name.

        Returns
        -------
        :class:`pyedb.dotnet.edb_core.materials.Material`
        """
        if name in self.__materials:
            raise ValueError(f"Material {name} already exists in material library.")

        material_def = self.__edb_definition.MaterialDef.Create(self.__edb.active_db, name)
        material = Material(self.__edb, material_def)

        attributes_input_dict = {key: val for (key,val) in kwargs.items() if key in ATTRIBUTES}
        if attributes_input_dict:
            material.update(attributes_input_dict)
        dc_attributes_input_dict = {key: val for (key,val) in kwargs.items() if key in DC_ATTRIBUTES}
        if dc_attributes_input_dict:
            material.update(dc_attributes_input_dict)

        self.__materials[name] = material
        return material

    @pyedb_function_handler()
    def add_conductor_material(self, name, conductivity, **kwargs):
        """Add a new conductor material.

        Parameters
        ----------
        name : str
            Name of the new material.
        conductivity : str, float, int
            Conductivity of the new material.

        Returns
        -------
        :class:`pyedb.dotnet.edb_core.materials.Material`

        """
        if name in self.__materials:
            raise ValueError(f"Material {name} already exists in material library.")

        extended_kwargs = {key: value for (key,value) in kwargs.items()}
        extended_kwargs["conductivity": conductivity]
        material = self.add_material(name, **extended_kwargs)
        self.__materials[name] = material
        return material

    @pyedb_function_handler()
    def add_dielectric_material(self, name, permittivity, dielectric_loss_tangent, **kwargs):
        """Add a new dielectric material in library.

        Parameters
        ----------
        name : str
            Name of the new material.
        permittivity : str, float, int
            Permittivity of the new material.
        dielectric_loss_tangent : str, float, int
            Dielectric loss tangent of the new material.

        Returns
        -------
        :class:`pyedb.dotnet.edb_core.materials.Material`
        """
        if name in self.__materials:
            raise ValueError(f"Material {name} already exists in material library.")

        extended_kwargs = {key: value for (key,value) in kwargs.items()}
        extended_kwargs["permittivity": permittivity]
        extended_kwargs["dielectric_loss_tangent": dielectric_loss_tangent]
        material = self.add_material(name, **extended_kwargs)
        return material

    # @pyedb_function_handler()
    # def get_material_djordjevicsarkar_model(self, name):
    #     """Get material Djordjevic-Sarkar model if any.

    #     Parameters
    #     ----------
    #     material_name : str

    #     Returns
    #     -------
    #     Any
    #     """
    #     material = self.materials[name]
    #     return material.dc_model

    @pyedb_function_handler()
    def add_djordjevicsarkar_dielectric(
        self,
        name,
        permittivity_at_frequency,
        loss_tangent_at_frequency,
        dielectric_model_frequency,
        dc_conductivity=None,
        dc_permittivity=None,
        **kwargs,
    ):
        """Add a dielectric using the Djordjevic-Sarkar model.

        Parameters
        ----------
        name : str
            Name of the dielectric.
        permittivity_at_frequency : str, float, int
            Relative permittivity of the dielectric.
        loss_tangent_at_frequency : str, float, int
            Loss tangent for the material.
        dielectric_model_frequency : str, float, int
            Test frequency in GHz for the dielectric.

        Returns
        -------
        :class:`pyedb.dotnet.edb_core.materials.Material`
        """
        if name in self.__materials:
            raise ValueError(f"Material {name} already exists in material library.")

        material_model = self.__edb_definition.DjordjecvicSarkarModel()
        material_model.SetRelativePermitivityAtFrequency(permittivity_at_frequency)
        material_model.SetLossTangentAtFrequency(self.__edb_value(loss_tangent_at_frequency))
        material_model.SetFrequency(dielectric_model_frequency)
        if dc_conductivity is not None:
            material_model.SetDCConductivity(dc_conductivity)
        if dc_permittivity is not None:
            material_model.SetUseDCRelativePermitivity(True)
            material_model.SetDCRelativePermitivity(dc_permittivity)
        try:
            material = self.__add_dielectric_material_model(name, material_model)
            for key, value in kwargs.items():
                setattr(material, key, value)
            self.__materials[name] = material
            return material
        except MaterialModelException:
            raise ValueError("Use realistic values to define DS model.")

    @pyedb_function_handler()
    def add_debye_material(
        self,
        name,
        permittivity_low,
        permittivity_high,
        loss_tangent_low,
        loss_tangent_high,
        lower_freqency,
        higher_frequency,
        **kwargs,
    ):
        """Add a dielectric with the Debye model.

        Parameters
        ----------
        name : str
            Name of the dielectric.
        permittivity_low : float, int
            Relative permittivity of the dielectric at the frequency specified
            for ``lower_frequency``.
        permittivity_high : float, int
            Relative permittivity of the dielectric at the frequency specified
            for ``higher_frequency``.
        loss_tangent_low : float, int
            Loss tangent for the material at the frequency specified
            for ``lower_frequency``.
        loss_tangent_high : float, int
            Loss tangent for the material at the frequency specified
            for ``higher_frequency``.
        lower_freqency : str, float, int
            Value for the lower frequency.
        higher_frequency : str, float, int
            Value for the higher frequency.

        Returns
        -------
        :class:`pyedb.dotnet.edb_core.materials.Material`
        """
        if name in self.__materials:
            raise ValueError(f"Material {name} already exists in material library.")

        material_model = self.__edb_definition.DebyeModel()
        # FIXME: Seems like there is a bug here (we need to provide higher value for
        # lower_freqency than higher_frequency)
        material_model.SetFrequencyRange(lower_freqency, higher_frequency)
        material_model.SetLossTangentAtHighLowFrequency(loss_tangent_low, loss_tangent_high)
        material_model.SetRelativePermitivityAtHighLowFrequency(
            self.__edb_value(permittivity_low), self.__edb_value(permittivity_high)
        )
        try:
            material = self.__add_dielectric_material_model(name, material_model)
            for key, value in kwargs.items():
                setattr(material, key, value)
            self.__materials[name] = material
            return material
        except MaterialModelException:
            raise ValueError("Use realistic values to define Debye model.")

    @pyedb_function_handler()
    def add_multipole_debye_material(
        self,
        name,
        frequencies,
        permittivities,
        loss_tangents,
        **kwargs,
    ):
        """Add a dielectric with the Multipole Debye model.

        Parameters
        ----------
        name : str
            Name of the dielectric.
        frequencies : list
            Frequencies in GHz.
        permittivities : list
            Relative permittivities at each frequency.
        loss_tangents : list
            Loss tangents at each frequency.

        Returns
        -------
        :class:`pyedb.dotnet.edb_core.materials.Material`

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb()
        >>> freq = [0, 2, 3, 4, 5, 6]
        >>> rel_perm = [1e9, 1.1e9, 1.2e9, 1.3e9, 1.5e9, 1.6e9]
        >>> loss_tan = [0.025, 0.026, 0.027, 0.028, 0.029, 0.030]
        >>> diel = edb.materials.add_multipole_debye_material("My_MP_Debye", freq, rel_perm, loss_tan)
        """
        if name in self.__materials:
            raise ValueError(f"Material {name} already exists in material library.")

        frequencies = [float(i) for i in frequencies]
        permittivities = [float(i) for i in permittivities]
        loss_tangents = [float(i) for i in loss_tangents]
        material_model = self.__edb_definition.MultipoleDebyeModel()
        material_model.SetParameters(
            convert_py_list_to_net_list(frequencies),
            convert_py_list_to_net_list(permittivities),
            convert_py_list_to_net_list(loss_tangents),
        )
        try:
            material = self.__add_dielectric_material_model(name, material_model)
            for key, value in kwargs.items():
                setattr(material, key, value)
            self.__materials[name] = material
            return material
        except MaterialModelException:
            raise ValueError("Use realistic values to define Multipole Debye model.")

    @pyedb_function_handler()
    def __add_dielectric_material_model(self, name, material_model):
        """Add a dielectric material model.

        Parameters
        ----------
        name : str
            Name of the dielectric.
        material_model : Any
            Dielectric material model.
        """
        if self.__edb_definition.MaterialDef.FindByName(self.__edb.active_db, name).IsNull():
            self.__edb_definition.MaterialDef.Create(self.__edb.active_db, name)
        material_def = self.__edb_definition.MaterialDef.FindByName(self.__edb.active_db, name)
        succeeded = material_def.SetDielectricMaterialModel(material_model)
        if succeeded:
            material = Material(self.__edb, material_def)
            return material
        raise MaterialModelException("Set dielectric material model failed.")

    @pyedb_function_handler()
    def duplicate(self, material_name, new_material_name):
        """Duplicate a material from the database.

        Parameters
        ----------
        material_name : str
            Name of the existing material.
        new_material_name : str
            Name of the new duplicated material.

        Returns
        -------
        :class:`pyedb.dotnet.edb_core.materials.Material`
        """
        if new_material_name in self.__materials:
            raise ValueError(f"Material {new_material_name} already exists in material library.")

        material = self.materials[material_name]
        material_model = material.dc_model
        material_def = self.__edb_definition.MaterialDef.Create(self.__edb.active_db, new_material_name)
        material_def.SetDielectricMaterialModel(material_model)
        new_material = Material(self.__edb, material_def)
        for attribute in ATTRIBUTES:
            value = getattr(material, attribute)
            setattr(new_material, attribute, value)

        if new_material.dc_model:
            for attribute in DC_ATTRIBUTES:
                value = getattr(material, attribute)
                if attribute == "dc_permittivity" and value is not None:
                    new_material.dc_model.SetUseDCRelativePermitivity(True)
                setattr(new_material, attribute, value)

        self.__materials[new_material_name] = new_material
        return new_material

    @pyedb_function_handler()
    def delete_material(self, material_name):
        """Remove a material from the database."""
        material_def = self.__edb_definition.MaterialDef.FindByName(self.__edb.active_db, material_name)
        if material_def.IsNull():
            raise ValueError(f"Cannot find material {material_name}.")
        material_def.Delete()
        del self.__materials[material_name]

    def update_material(self, material_name, input_dict):
        material = self[material_name]
        attributes_input_dict = {key: val for (key,val) in input_dict.items() if key in ATTRIBUTES}
        if attributes_input_dict:
            material.update(attributes_input_dict)

        dc_attributes_input_dict = {key: val for (key,val) in input_dict.items() if key in DC_ATTRIBUTES}
        if dc_attributes_input_dict:
            material.update(dc_attributes_input_dict)

        self.__materials[material_name] = material
        return material

    # @pyedb_function_handler()
    # def load_material(self, material):
    #     """
    #     """
    #     if self.materials:
    #         mat_keys = [i.lower() for i in self.materials.keys()]
    #         mat_keys_case = [i for i in self.materials.keys()]
    #     else:
    #         mat_keys = []
    #         mat_keys_case = []

    #     if not material:
    #         return
    #     if material["name"].lower() not in mat_keys:
    #         if "conductivity" not in material:
    #             self.add_dielectric_material(material["name"], material["permittivity"], material["loss_tangent"])
    #         elif material["conductivity"] > 1e4:
    #             self.add_conductor_material(material["name"], material["conductivity"])
    #         else:
    #             self.add_dielectric_material(material["name"], material["permittivity"], material["loss_tangent"])
    #         self.materials[material["name"]]._load(material)
    #     else:
    #         self.materials[mat_keys_case[mat_keys.index(material["name"].lower())]]._load(material)

    @pyedb_function_handler()
    def material_property_to_id(self, property_name):
        """Convert a material property name to a material property ID.

        Parameters
        ----------
        property_name : str
            Name of the material property.

        Returns
        -------
        Any
        """
        material_property_id = self.__edb_definition.MaterialPropertyId
        property_name_to_id = {
            "Permittivity": material_property_id.Permittivity,
            "Permeability": material_property_id.Permeability,
            "Conductivity": material_property_id.Conductivity,
            "DielectricLossTangent": material_property_id.DielectricLossTangent,
            "MagneticLossTangent": material_property_id.MagneticLossTangent,
            "ThermalConductivity": material_property_id.ThermalConductivity,
            "MassDensity": material_property_id.MassDensity,
            "SpecificHeat": material_property_id.SpecificHeat,
            "YoungsModulus": material_property_id.YoungsModulus,
            "PoissonsRatio": material_property_id.PoissonsRatio,
            "ThermalExpansionCoefficient": material_property_id.ThermalExpansionCoefficient,
            "InvalidProperty": material_property_id.InvalidProperty,
        }

        match = difflib.get_close_matches(property_name, property_name_to_id, 1, 0.7)
        if match:
            return property_name_to_id[match[0]]
        else:
            return property_name_to_id["InvalidProperty"]

    # @pyedb_function_handler()
    def load_amat(self, amat_file):
        """Load materials from an AMAT file.

        Parameters
        ----------
        amat_file : str
            Full path to the AMAT file to read and add to the Edb.

        Returns
        -------
        bool
        """
        if not os.path.exists(amat_file):
            raise FileNotFoundError(f"File path {amat_file} does not exist.")
        materials_dict = self.read_materials(amat_file)
        for material_name, material_properties in materials_dict.items():
            if not material_name in self:
                # FIXME: Shouldn't we remove that if statement ?
                if "tangent_delta" in material_properties:
                    material_properties["dielectric_loss_tangent"] = material_properties["tangent_delta"]
                    del material_properties["tangent_delta"]
                self.add_material(material_name, **material_properties)
            else:
                self.__edb.logger.warning(f"Material {material_name} already exist and was not loaded from AMAT file.")
        return True

    @staticmethod
    @pyedb_function_handler()
    def read_materials(amat_file):
        """Read materials from an AMAT file.

        Parameters
        ----------
        amat_file : str
            Full path to the AMAT file to read.

        Returns
        -------
        dict
            {material name: dict of material properties}.
        """

        def get_line_float_value(line):
            """Retrieve the float value expected in the line of an AMAT file.

            The associated string is expected to follow one of the following cases:
            - simple('permittivity', 12.)
            - permittivity='12'.
            """
            try:
                return float(re.split(",|=", line)[-1].strip(")'"))
            except ValueError:
                return None

        res = {}
        _begin_search = re.compile(r"^\$begin '(.+)'")
        _end_search = re.compile(r"^\$end '(.+)'")
        material_properties = [
            "thermal_conductivity",
            "permittivity",
            "dielectric_loss_tangent",
            "permeability",
            "magnetic_loss_tangent",
            "thermal_expansion_coeffcient",
            "specific_heat",
            "mass_density",
        ]

        with open(amat_file, "r") as amat_fh:
            raw_lines = amat_fh.read().splitlines()
            material_name = ""
            for line in raw_lines:
                b = _begin_search.search(line)
                if b:  # walk down a level
                    material_name = b.group(1)
                    res.setdefault(material_name, {})
                    if len(res) > 165:
                        pass
                if material_name:
                    for material_property in material_properties:
                        if material_property in line:
                            value = get_line_float_value(line)
                            if value is not None:
                                res[material_name][material_property] = value
                            break
                    # Extra case to avoid confusion ("conductivity" is included in "thermal_conductivity")
                    if "conductivity" in line and "thermal_conductivity" not in line:
                        value = get_line_float_value(line)
                        if value is not None:
                            res[material_name]["conductivity"] = value
                end = _end_search.search(line)
                if end:
                    material_name = ""

        # Clean unwanted data
        for key in ("$index$", "$base_index$"):
            if key in res:
                del res[key]

        return res


if __name__ == "__main__":
    edb = Edb()
    materials = Materials(edb)
    mat_file = os.path.join(edb.base_path, "syslib", "Materials.amat")
    assert materials.load_amat(mat_file)
