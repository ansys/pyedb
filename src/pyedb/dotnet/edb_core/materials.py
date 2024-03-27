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

from pyedb import Edb
from pyedb.dotnet.clr_module import _clr
from pyedb.dotnet.edb_core.general import convert_py_list_to_net_list
from pyedb.generic.general_methods import is_ironpython, pyedb_function_handler
from pydantic import BaseModel

logger = logging.getLogger(__name__)

from pydantic import BaseModel, confloat
from typing import Optional, Union
  
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

class MaterialProperties(BaseModel):
    """Store material properties."""
    conductivity : Optional[PositiveFloat] = None
    dielectric_loss_tangent : Optional[PositiveFloat] = None
    magnetic_loss_tangent : Optional[PositiveFloat] = None
    mass_density : Optional[PositiveFloat] = None
    permittivity : Optional[PositiveFloat] = None
    permeability : Optional[PositiveFloat] = None
    poisson_ratio : Optional[PositiveFloat] = None
    specific_heat : Optional[PositiveFloat] = None
    thermal_conductivity : Optional[PositiveFloat] = None
    youngs_modulus : Optional[PositiveFloat] = None
    thermal_expansion_coefficient : Optional[PositiveFloat] = None
    dc_conductivity : Optional[PositiveFloat] = None
    dc_permittivity : Optional[PositiveFloat] = None
    dielectric_model_frequency : Optional[PositiveFloat] = None
    loss_tangent_at_frequency : Optional[PositiveFloat] = None
    permittivity_at_frequency : Optional[PositiveFloat] = None

class DjordjevicSarkarMaterialAddEvent(BaseModel):
    """Store Djordjevic-Sarkar properties"""
    name: str
    dc_conductivity : Optional[PositiveFloat] = None
    dc_permittivity : Optional[PositiveFloat] = None
    dielectric_model_frequency : Optional[PositiveFloat] = None
    loss_tangent_at_frequency : Optional[PositiveFloat] = None
    permittivity_at_frequency : Optional[PositiveFloat] = None

class MaterialModelException(Exception):
    """Exception triggered when handling material model."""

class Material(object):
    """Manage EDB methods for material property management."""

    def __init__(self, edb: Edb, material_def):
        self.__edb: Edb = edb
        self.__name: str = material_def.GetName()
        self.__material_def = material_def
        self.__dc_model = material_def.GetDielectricMaterialModel()
        self.__properties : MaterialProperties = MaterialProperties()
        self.__observers = []

    @property
    def name(self):
        """Material name."""
        return self.__name

    @property
    def dc_model(self):
        """Material dielectric model."""
        return self.__dc_model

    @pyedb_function_handler()
    def property_value(self, material_property_id):
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

    @property
    def conductivity(self):
        """Get material conductivity."""
        if self.__properties.conductivity is None:
            material_property_id = self.__edb.edb_api.definition.MaterialPropertyId.Conductivity
            self.__properties.conductivity = self.property_value(material_property_id)
        return self.__properties.conductivity

    @conductivity.setter
    def conductivity(self, value):
        """Set material conductivity."""
        edb_value = self.__edb_value(value)
        material_property_id = self.__edb.edb_api.definition.MaterialPropertyId.Conductivity
        self.__material_def.SetProperty(material_property_id, self.__edb_value(value))
        self.__properties.conductivity = edb_value.ToDouble()

    @property
    def permittivity(self):
        """Get material permittivity."""
        if self.__properties.permittivity is None:
            material_property_id = self.__edb.edb_api.definition.MaterialPropertyId.Permittivity
            self.__properties.permittivity = self.property_value(material_property_id)
        return self.__properties.permittivity

    @permittivity.setter
    def permittivity(self, value):
        """Set material permittivity."""
        edb_value = self.__edb_value(value)
        material_property_id = self.__edb.edb_api.definition.MaterialPropertyId.Permittivity
        self.__material_def.SetProperty(material_property_id, edb_value)
        self.__properties.permittivity = edb_value.ToDouble()

    @property
    def permeability(self):
        """Get material permeability."""
        if self.__properties.permeability is None:
            material_property_id = self.__edb.edb_api.definition.MaterialPropertyId.Permeability
            self.__properties.permeability = self.property_value(material_property_id)
        return self.__properties.permeability

    @permeability.setter
    def permeability(self, value):
        """Set material permeability."""
        edb_value = self.__edb_value(value)
        material_property_id = self.__edb.edb_api.definition.MaterialPropertyId.Permeability
        self.__material_def.SetProperty(material_property_id, edb_value)
        self.__properties.permeability = edb_value.ToDouble()

    @property
    def dielectric_loss_tangent(self):
        """Get material loss tangent."""
        if self.__properties.loss_tangent is None:
            material_property_id = self.__edb.edb_api.definition.MaterialPropertyId.DielectricLossTangent
            self.__properties.loss_tangent = self.property_value(material_property_id)
        return self.__properties.loss_tangent

    @dielectric_loss_tangent.setter
    def dielectric_loss_tangent(self, value):
        """Set material loss tangent."""
        edb_value = self.__edb_value(value)
        material_property_id = self.__edb.edb_api.definition.MaterialPropertyId.DielectricLossTangent
        self.__material_def.SetProperty(material_property_id, edb_value)
        self.__properties.dielectric_loss_tangent = edb_value.ToDouble()

    @property
    def dc_conductivity(self):
        """Get material dielectric conductivity."""
        if self.__dc_model and self.__properties.dc_conductivity is None:
            self.__properties.dc_conductivity = self.__dc_model.GetDCConductivity()
        return self.__properties.dc_conductivity

    @dc_conductivity.setter
    def dc_conductivity(self, value):
        """Set material dielectric conductivity."""
        if self.__dc_model:
            edb_value = self.__edb_value(value)
            self.__dc_model.SetDCConductivity(edb_value)
            self.__properties.dc_conductivity = edb_value.ToDouble()

    @property
    def dc_permittivity(self):
        """Get material dielectric relative permittivity"""
        if self.__dc_model and self.__properties.dc_permittivity is None:
            self.__properties.dc_permittivity = self.__dc_model.GetDCRelativePermitivity()
        return self.__properties.dc_permittivity

    @dc_permittivity.setter
    def dc_permittivity(self, value):
        """Set material dielectric relative permittivity"""
        if self.__dc_model:
            edb_value = self.__edb_value(value)
            self.__dc_model.SetDCRelativePermitivity(edb_value)
            self.__properties.dc_permittivity = edb_value.ToDouble()

    @property
    def dielectric_model_frequency(self):
        """Get material frequency in GHz."""
        if self.__dc_model and self.__properties.dielectric_model_frequency is None:
            self.__properties.dielectric_model_frequency = self.__dc_model.GetFrequency()
        return self.__properties.dielectric_model_frequency


    @dielectric_model_frequency.setter
    def dielectric_model_frequency(self, value):
        """Get material frequency in GHz."""
        if self.__dc_model:
            edb_value = self.__edb_value(value)
            self.__dc_model.SetFrequency(edb_value)
            self.__properties.dielectric_model_frequency = edb_value.ToDouble()

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
    def permittivity_at_frequency(self, value):
        """Set material relative permittivity at frequency."""
        if self.__dc_model:
            edb_value = self.__edb_value(value)
            self.__dc_model.SetRelativePermitivityAtFrequency(edb_value)
            self.__properties.permittivity_at_frequency = edb_value.ToDouble()

    @property
    def magnetic_loss_tangent(self):
        """Get material magnetic loss tangent."""
        if self.__properties.magnetic_loss_tangent is None:
            material_property_id = self.__edb.edb_api.definition.MaterialPropertyId.MagneticLossTangent
            self.__properties.magnetic_loss_tangent = self.property_value(material_property_id)
        return self.__properties.magnetic_loss_tangent

    @magnetic_loss_tangent.setter
    def magnetic_loss_tangent(self, value):
        """Set material magnetic loss tangent."""
        edb_value = self.__edb_value(value)
        material_property_id = self.__edb.edb_api.definition.MaterialPropertyId.MagneticLossTangent
        self.__material_def.SetProperty(material_property_id, edb_value)
        self.__properties.magnetic_loss_tangent = edb_value.ToDouble()

    @property
    def thermal_conductivity(self):
        """Get material thermal conductivity."""
        if self.__properties.thermal_conductivity is None:
            material_property_id = self.__edb.edb_api.definition.MaterialPropertyId.ThermalConductivity
            self.__properties.thermal_conductivity = self.property_value(material_property_id)
        return self.__properties.thermal_conductivity

    @thermal_conductivity.setter
    def thermal_conductivity(self, value):
        """Set material thermal conductivity."""
        edb_value = self.__edb_value(value)
        material_property_id = self.__edb.edb_api.definition.MaterialPropertyId.ThermalConductivity
        self.__material_def.SetProperty(material_property_id, edb_value)
        self.__properties.thermal_conductivity = edb_value.ToDouble()

    @property
    def mass_density(self):
        """Get material mass density."""
        if self.__properties.thermal_conductivity is None:
            material_property_id = self.__edb.edb_api.definition.MaterialPropertyId.MassDensity
            self.__properties.mass_density = self.property_value(material_property_id)
        return self.__properties.mass_density

    @mass_density.setter
    def mass_density(self, value):
        """Set material mass density."""
        edb_value = self.__edb_value(value)
        material_property_id = self.__edb.edb_api.definition.MaterialPropertyId.MassDensity
        self.__material_def.SetProperty(material_property_id, edb_value)
        self.__properties.mass_density = edb_value.ToDouble()

    @property
    def youngs_modulus(self):
        """Get material youngs modulus."""
        if self.__properties.youngs_modulus is None:
            material_property_id = self.__edb.edb_api.definition.MaterialPropertyId.YoungsModulus
            self.__properties.youngs_modulus = self.property_value(material_property_id)
        return self.__properties.youngs_modulus

    @youngs_modulus.setter
    def youngs_modulus(self, value):
        """Set material youngs modulus."""
        edb_value = self.__edb_value(value)
        material_property_id = self.__edb.edb_api.definition.MaterialPropertyId.YoungsModulus
        self.__material_def.SetProperty(material_property_id, edb_value)
        self.__properties.youngs_modulus = edb_value.ToDouble()

    @property
    def specific_heat(self):
        """Get material specific heat."""
        if self.__properties.specific_heat is None:
            material_property_id = self.__edb.edb_api.definition.MaterialPropertyId.SpecificHeat
            self.__properties.specific_heat = self.property_value(material_property_id)
        return self.__properties.specific_heat

    @specific_heat.setter
    def specific_heat(self, value):
        """Set material specific heat."""
        edb_value = self.__edb_value(value)
        material_property_id = self.__edb.edb_api.definition.MaterialPropertyId.SpecificHeat
        self.__material_def.SetProperty(material_property_id, edb_value)
        self.__properties.specific_heat = edb_value.ToDouble()

    @property
    def poisson_ratio(self):
        """Get material poisson ratio."""
        if self.__properties.specific_heat is None:
            material_property_id = self.__edb.edb_api.definition.MaterialPropertyId.PoissonsRatio
            self.__properties.poisson_ratio = self.property_value(material_property_id)
        return self.__properties.poisson_ratio

    @poisson_ratio.setter
    def poisson_ratio(self, value):
        """Set material poisson ratio."""
        edb_value = self.__edb_value(value)
        material_property_id = self.__edb.edb_api.definition.MaterialPropertyId.PoissonsRatio
        self.__material_def.SetProperty(material_property_id, edb_value)
        self.__properties.poisson_ratio = edb_value.ToDouble()

    @property
    def thermal_expansion_coefficient(self):
        """Get material thermal coefficient."""
        if self.__properties.thermal_expansion_coefficient is None:
            material_property_id = self.__edb.edb_api.definition.MaterialPropertyId.ThermalExpansionCoefficient
            self.__properties.thermal_expansion_coefficient = self.property_value(material_property_id)
        return self.__properties.thermal_expansion_coefficient

    @thermal_expansion_coefficient.setter
    def thermal_expansion_coefficient(self, value):
        """Set material thermal coefficient."""
        edb_value = self.__edb_value(value)
        material_property_id = self.__edb.edb_api.definition.MaterialPropertyId.ThermalExpansionCoefficient
        self.__material_def.SetProperty(material_property_id, self.__edb_value(value))
        self.__properties.thermal_expansion_coefficient = edb_value.ToDouble()

    def add_observer(self, observer):
        """Add an observer.
        """
        self.__observers.append(observer)

    def notify(self, data: dict):
        """Notify observers about the addition of a DjordjevicSarkar material."""
        event = DjordjevicSarkarMaterialAddEvent(data)
        for observer in self.__observers:
            observer.update(event)

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
            attributes = ["conductivity", "dielectric_loss_tangent", "magnetic_loss_tangent", "mass_density",
                          "permittivity", "permeability", "poisson_ratio", "specific_heat",
                          "thermal_conductivity", "youngs_modulus", "thermal_expansion_coefficient"]
            for attribute in attributes:
                if attribute in input_dict:
                    setattr(self, attribute, input_dict[attribute])

            dc_attributes = ["dielectric_model_frequency", "loss_tangent_at_frequency", "permittivity_at_frequency", "dc_conductivity", "dc_permittivity"]
            # Update DS model
            # NOTE: Contrary to before we don't test 'dielectric_model_frequency' only
            if any(map(lambda attribute: input_dict.get(attribute, None) is not None, dc_attributes)):
                if self.__dc_model:
                    for attribute in dc_attributes:
                        if attribute in input_dict:
                            if attribute == "dc_permittivity" and input_dict[attribute] is not None:
                                self.__dc_model.SetUseDCRelativePermitivity(True)
                            setattr(self, attribute, input_dict[attribute])
                else:
                    data = {attribute: input_dict.get(attribute, None) for attribute in dc_attributes}
                    data["name"] = self.name
                    self.notify(data)
            # Unset DS model if it is already assigned to the material in the database
            elif self.__dc_model:
                self.__material_def.SetDielectricMaterialModel(self.__edb_value(None))

    def __edb_value(self, value):
        """Convert a value to an EDB value.

        Parameters
        ----------
        val : str, float, int
        """
        return self.__edb.edb_value(value)

    def __load_all_properties(self):
        """Load all properties of the material.
        """
        for property in self.__properties.model_dump().keys():
            _ = getattr(self, property)

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
        self.__syslib = os.path.join(self.__edb.base_path, "syslib")
        self.__materials: dict[str, Material] = {
            material_def.GetName(): Material(self, material_def) for material_def in list(self.__edb.active_db.MaterialDefs)
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

    def update(self, event: DjordjevicSarkarMaterialAddEvent):
        try:
            self.add_djordjevicsarkar_dielectric(event.name,
                                                 event.permittivity_at_frequency,
                                                 event.loss_tangent_at_frequency,
                                                 event.dielectric_model_frequency,
                                                 event.dc_conductivity,
                                                 event.dc_permittivity
            )
        except ValueError:
            raise MaterialModelException(f"Cannot set DS model for material {event.name}." \
                                      "Check for realistic values that define DS model.")

    # def __db(self):
    #     return self.__edb.active_db
    # @pyedb_function_handler()
    # def _edb_value(self, value):
    #     return self._pedb.edb_value(value)

#     @property
#     def _edb(self):
#         return self._pedb.edb_api

#     @property
#     def _db(self):
#         return self._pedb.active_db

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
    def add_material(self, name:str, **kwargs):
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

        material_def = self.__edb.edb_api.definition.MaterialDef.Create(self.__edb.active_db, name)
        material = Material(self.__edb, material_def)
        for key, value in kwargs.items():
            setattr(material, key, value)
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

        material_def = self.__edb.edb_api.definition.MaterialDef.Create(self.__edb.active_db, name)
        material = Material(self.__edb, material_def)
        material.conductivity = self.__edb_value(conductivity)
        for key, value in kwargs.items():
            setattr(material, key, value)
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

        material_def = self.__edb.edb_api.definition.MaterialDef.Create(self.__edb.active_db, name)
        material = Material(self.__edb, material_def)
        material.permittivity = self.__edb_value(permittivity)
        material.dielectric_loss_tangent = dielectric_loss_tangent
        for key, value in kwargs.items():
            setattr(material, key, value)
        self.__materials[name] = material
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
    def add_djordjevicsarkar_dielectric(self, name, permittivity_at_frequency, loss_tangent_at_frequency, dielectric_model_frequency, dc_conductivity=None, dc_permittivity=None, **kwargs):
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
        material_model = self.__edb.edb_api.definition.DjordjecvicSarkarModel()
        material_model.SetRelativePermitivityAtFrequency(self.__edb_value(permittivity_at_frequency))
        material_model.SetLossTangentAtFrequency(self.__edb_value(loss_tangent_at_frequency))
        material_model.SetFrequency(self.__edb_value(dielectric_model_frequency))
        if dc_conductivity is not None:
            material_model.SetDCConductivity(self.__edb_value(dc_conductivity))
        if dc_permittivity is not None:
            material_model.SetUseDCRelativePermitivity(True)
            material_model.SetDCRelativePermitivity(self.__edb_value(dc_permittivity))
        try:
            material_def = self.__add_dielectric_material_model(name, material_model)
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
        permittivity_low : str, float, int
            Relative permittivity of the dielectric at the frequency specified
            for ``lower_frequency``.
        permittivity_high : str, float, int
            Relative permittivity of the dielectric at the frequency specified
            for ``higher_frequency``.
        loss_tangent_low : str, float, int
            Loss tangent for the material at the frequency specified
            for ``lower_frequency``.
        loss_tangent_high : str, float, int
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
        material_model = self.__edb.edb_api.definition.DebyeModel()
        material_model.SetFrequencyRange(self.__edb_value(lower_freqency), self.__edb_value(higher_frequency))
        material_model.SetLossTangentAtHighLowFrequency(self.__edb_value(loss_tangent_low), self.__edb_value(loss_tangent_high))
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
        frequencies = [self.__edb_value(i) for i in frequencies]
        permittivities = [self.__edb_value(i) for i in permittivities]
        loss_tangents = [self.__edb_value(i) for i in loss_tangents]
        material_def = self.__edb.edb_api.definition.MultipoleDebyeModel()
        material_def.SetParameters(
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
        if self.__edb.edb_api.definition.MaterialDef.FindByName(self.__edb.active_db, name).IsNull():
            self.__edb.edb_api.definition.MaterialDef.Create(self.__edb.active_db, name)
        material_def = self.__edb.edb_api.definition.MaterialDef.FindByName(self.__edb.active_db, name)
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
        material = self.materials[material_name]
        attributes = ["conductivity", "dielectric_loss_tangent", "magnetic_loss_tangent", "mass_density",
                "permittivity", "permeability", "poisson_ratio", "specific_heat",
                "thermal_conductivity", "youngs_modulus", "thermal_expansion_coefficient"]
        material_model = material.dc_model
        material_def = self.__edb.edb_api.definition.MaterialDef.Create(self.__edb.active_db, new_material_name)
        material_def.SetDielectricMaterialModel(material_model)
        new_material = Material(self.__edb, material_def)
        for attribute in attributes:
            value = getattr(material, attribute)
            setattr(new_material, attribute, value)

        dc_attributes = ["dielectric_model_frequency", "loss_tangent_at_frequency", "permittivity_at_frequency", "dc_conductivity", "dc_permittivity"]
        if new_material.dc_model:
            for attribute in dc_attributes:
                value = getattr(material, attribute)
                if attribute == "dc_permittivity" and value is not None:
                    new_material.dc_model.SetUseDCRelativePermitivity(True)
                setattr(new_material, attribute, value)

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
        material_property_id = self.__edb.edb_api.definition.MaterialPropertyId
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
    # def material_property(self, material_name, property_name):
    #     """Get the property of a material. If it is executed in IronPython,
    #      you must only use the first element of the returned tuple, which is a float.

    #     Parameters
    #     ----------
    #     material_name : str
    #         Name of the existing material.
    #     property_name : str
    #         Name of the material property.
    #         ``permittivity``
    #         ``permeability``
    #         ``conductivity``
    #         ``dielectric_loss_tangent``
    #         ``magnetic_loss_tangent``

    #     Returns
    #     -------
    #     float
    #         The float value of the property.


    #     Examples
    #     --------
    #     >>> from pyedb import Edb
    #     >>> edb_app = Edb()
    #     >>> returned_tuple = edb_app.materials.get_property_by_material_name("conductivity", "copper")
    #     >>> edb_value = returned_tuple[0]
    #     >>> float_value = returned_tuple[1]

    #     """
    #     if self._edb.definition.MaterialDef.FindByName(self._pedb._db, material_name).IsNull():
    #         self._pedb.logger.error("This material doesn't exists.")
    #     else:
    #         original_material = self._edb.definition.MaterialDef.FindByName(self._pedb._db, material_name)
    #         if is_ironpython:  # pragma: no cover
    #             property_box = _clr.StrongBox[float]()
    #             original_material.GetProperty(self.material_name_to_id(property_name), property_box)
    #             return float(property_box)
    #         else:
    #             _, property_box = original_material.GetProperty(
    #                 self.material_name_to_id(property_name), self.__edb_value(0.0)
    #             )
    #             if isinstance(property_box, float):
    #                 return property_box
    #             else:
    #                 return property_box.ToDouble()
    #     return False

    @pyedb_function_handler()
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
                if "tangent_delta" in material_properties:
                    material_properties["dielectric_loss_tangent"] = material_properties["tangent_delta"]
                    del material_properties["tangent_delta"]
                self.add_material(name=material_name, **material_properties)
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
                if material_name:
                    for material_property in material_properties:
                        if material_property in line:
                            value = get_line_float_value(line)
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

