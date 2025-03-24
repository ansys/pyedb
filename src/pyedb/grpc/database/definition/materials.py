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
from typing import Optional
import warnings

from ansys.edb.core.definition.debye_model import DebyeModel as GrpcDebyeModel
from ansys.edb.core.definition.djordjecvic_sarkar_model import (
    DjordjecvicSarkarModel as GrpcDjordjecvicSarkarModel,
)
from ansys.edb.core.definition.material_def import (
    MaterialProperty as GrpcMaterialProperty,
)
from ansys.edb.core.definition.material_def import MaterialDef as GrpcMaterialDef
from ansys.edb.core.definition.multipole_debye_model import (
    MultipoleDebyeModel as GrpcMultipoleDebyeModel,
)
from ansys.edb.core.utility.value import Value as GrpcValue
from pydantic import BaseModel, confloat

from pyedb import Edb
from pyedb.exceptions import MaterialModelException

logger = logging.getLogger(__name__)

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
DC_ATTRIBUTES = [
    "dielectric_model_frequency",
    "loss_tangent_at_frequency",
    "permittivity_at_frequency",
    "dc_conductivity",
    "dc_permittivity",
]
PERMEABILITY_DEFAULT_VALUE = 1


def get_line_float_value(line):
    """Retrieve the float value expected in the line of an AMAT file.

    The associated string is expected to follow one of the following cases:
    - simple('permittivity', 12.)
    - permittivity='12'.
    """
    try:
        return float(re.split(",|=", line)[-1].strip("'\n)"))
    except ValueError:
        return None


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


class Material(GrpcMaterialDef):
    """Manage EDB methods for material property management."""

    def __init__(self, edb: Edb, edb_material_def):
        super().__init__(edb_material_def.msg)
        self.__edb: Edb = edb
        self.__name: str = edb_material_def.name
        self.__material_def = edb_material_def
        self.__dielectric_model = None

    @property
    def name(self):
        """Material name.

        Returns
        -------
        str
            Material name.
        """
        return self.__name

    @property
    def dc_model(self):
        """Dielectric material model.

        Returns
        -------
        :class:``

        """
        return self.dielectric_material_model

    @property
    def dielectric_material_model(self):
        """Material dielectric model.

        Returns
        -------
        :class:`DebyeModel <ansys.edb.core.definition.debye_model.DebyeModel>` or
        :class:`DjordjecvicSarkarModel <ansys.edb.core.definition.djordjecvic_sarkar_model.DjordjecvicSarkarModel>` or
        :class:`MultipoleDebyeModel <ansys.edb.core.definition.multipole_debye_model.MultipoleDebyeModel>`.
            EDB dielectric model.
        """
        try:
            if super().dielectric_material_model.type.name.lower() == "debye":
                self.__dielectric_model = GrpcDebyeModel(super().dielectric_material_model.msg)
            elif super().dielectric_material_model.type.name.lower() == "multipole_debye":
                self.__dielectric_model = GrpcMultipoleDebyeModel(super().dielectric_material_model.msg)
            elif super().dielectric_material_model.type.name.lower() == "djordjecvic_sarkar":
                self.__dielectric_model = GrpcDjordjecvicSarkarModel(super().dielectric_material_model.msg)
            return self.__dielectric_model
        except:
            return None

    @property
    def conductivity(self):
        """Get material conductivity.

        Returns
        -------
        float
         Conductivity value.
        """
        try:
            value = self.get_property(GrpcMaterialProperty.CONDUCTIVITY).value
            return value
        except:
            return None

    @conductivity.setter
    def conductivity(self, value):
        """Set material conductivity."""
        if self.dielectric_material_model:
            self.__edb.logger.error(
                f"Dielectric model defined on material {self.name}. Conductivity can not be changed"
                f"Changing conductivity is only allowed when no dielectric model is assigned."
            )
        else:
            self.set_property(GrpcMaterialProperty.CONDUCTIVITY, GrpcValue(value))

    @property
    def dc_conductivity(self):
        """Material DC conductivity.

        Returns
        -------
        float
            DC conductivity value.

        """
        try:
            return self.dielectric_material_model.dc_conductivity
        except:
            return

    @dc_conductivity.setter
    def dc_conductivity(self, value):
        if self.dielectric_material_model:
            self.dielectric_material_model.dc_conductivity = float(value)

    @property
    def dc_permittivity(self):
        """Material DC permittivity.

        Returns
        -------
        float
            DC permittivity value.

        """
        try:
            return self.dielectric_material_model.dc_relative_permitivity
        except:
            return

    @dc_permittivity.setter
    def dc_permittivity(self, value):
        if self.dielectric_material_model:
            self.dielectric_material_model.dc_relative_permitivity = float(value)

    @property
    def loss_tangent_at_frequency(self):
        """Material loss tangent at frequency if dielectric model is defined.

        Returns
        -------
        float
            Loss tangent value.

        """
        try:
            return self.dielectric_material_model.loss_tangent_at_frequency
        except:
            return

    @loss_tangent_at_frequency.setter
    def loss_tangent_at_frequency(self, value):
        if self.dielectric_material_model:
            self.dielectric_material_model.loss_tangent_at_frequency = float(value)

    @property
    def dielectric_model_frequency(self):
        """Dielectric model frequency if model is defined.

        Returns
        -------
        float
            Frequency value.

        """
        try:
            return self.dielectric_material_model.frequency
        except:
            return

    @dielectric_model_frequency.setter
    def dielectric_model_frequency(self, value):
        if self.dielectric_material_model:
            self.dielectric_material_model.frequency = float(value)

    @property
    def permittivity_at_frequency(self):
        """Material permittivity at frequency if model is defined.


        Returns
        -------
        float
            Permittivity value.

        """
        try:
            return self.dielectric_material_model.relative_permitivity_at_frequency
        except:
            return

    @permittivity_at_frequency.setter
    def permittivity_at_frequency(self, value):
        if self.dielectric_material_model:
            self.dielectric_material_model.relative_permitivity_at_frequency = float(value)

    @property
    def permittivity(self):
        """Material permittivity.


        Returns
        -------
        float
            Permittivity value.

        """
        try:
            value = self.get_property(GrpcMaterialProperty.PERMITTIVITY).value
            return value
        except:
            return None

    @permittivity.setter
    def permittivity(self, value):
        """Set material permittivity."""
        self.set_property(GrpcMaterialProperty.PERMITTIVITY, GrpcValue(value))

    @property
    def permeability(self):
        """Material permeability.

        Returns
        -------
        float
            Permeability value.

        """
        try:
            value = self.get_property(GrpcMaterialProperty.PERMEABILITY).value
            return value
        except:
            return None

    @permeability.setter
    def permeability(self, value):
        """Set material permeability."""
        self.set_property(GrpcMaterialProperty.PERMEABILITY, GrpcValue(value))

    @property
    def loss_tangent(self):
        """Material loss tangent.

        Returns
        -------
        float
            Loss tangent value.

        """
        warnings.warn(
            "This method is deprecated in versions >0.7.0 and will soon be removed. "
            "Use property dielectric_loss_tangent instead.",
            DeprecationWarning,
        )
        return self.dielectric_loss_tangent

    @property
    def dielectric_loss_tangent(self):
        """Material loss tangent.

        Returns
        -------
        float
            Loss tangent value.

        """
        try:
            return self.get_property(GrpcMaterialProperty.DIELECTRIC_LOSS_TANGENT).value
        except:
            return None

    @loss_tangent.setter
    def loss_tangent(self, value):
        """Set material loss tangent."""
        warnings.warn(
            "This method is deprecated in versions >0.7.0 and will soon be removed. "
            "Use property dielectric_loss_tangent instead.",
            DeprecationWarning,
        )
        self.dielectric_loss_tangent(value)

    @dielectric_loss_tangent.setter
    def dielectric_loss_tangent(self, value):
        """Set material loss tangent."""
        self.set_property(GrpcMaterialProperty.DIELECTRIC_LOSS_TANGENT, GrpcValue(value))

    @property
    def magnetic_loss_tangent(self):
        """Material magnetic loss tangent.

        Returns
        -------
        float
            Magnetic loss tangent value.
        """
        try:
            value = self.get_property(GrpcMaterialProperty.MAGNETIC_LOSS_TANGENT).value
            return value
        except:
            return None

    @magnetic_loss_tangent.setter
    def magnetic_loss_tangent(self, value):
        """Set material magnetic loss tangent."""
        self.set_property(GrpcMaterialProperty.MAGNETIC_LOSS_TANGENT, GrpcValue(value))

    @property
    def thermal_conductivity(self):
        """Material thermal conductivity.

        Returns
        -------
        float
            Thermal conductivity value.

        """
        try:
            value = self.get_property(GrpcMaterialProperty.THERMAL_CONDUCTIVITY).value
            return value
        except:
            return None

    @thermal_conductivity.setter
    def thermal_conductivity(self, value):
        """Set material thermal conductivity."""
        self.set_property(GrpcMaterialProperty.THERMAL_CONDUCTIVITY, GrpcValue(value))

    @property
    def mass_density(self):
        """Material mass density.

        Returns
        -------
        float
            Mass density value.

        """
        try:
            value = self.get_property(GrpcMaterialProperty.MASS_DENSITY).value
            return value
        except:
            return None

    @mass_density.setter
    def mass_density(self, value):
        """Set material mass density."""
        self.set_property(GrpcMaterialProperty.MASS_DENSITY, GrpcValue(value))

    @property
    def youngs_modulus(self):
        """Material young modulus.

        Returns
        -------
        float
            Material young modulus value.

        """
        try:
            value = self.get_property(GrpcMaterialProperty.YOUNGS_MODULUS).value
            return value
        except:
            return None

    @youngs_modulus.setter
    def youngs_modulus(self, value):
        """Set material young modulus."""
        self.set_property(GrpcMaterialProperty.YOUNGS_MODULUS, GrpcValue(value))

    @property
    def specific_heat(self):
        """Material specific heat.

        Returns
        -------
        float
            Material specific heat value.
        """
        try:
            return self.get_property(GrpcMaterialProperty.SPECIFIC_HEAT).value
        except:
            return None

    @specific_heat.setter
    def specific_heat(self, value):
        """Set material specific heat."""
        self.set_property(GrpcMaterialProperty.SPECIFIC_HEAT, GrpcValue(value))

    @property
    def poisson_ratio(self):
        """Material poisson ratio.

        Returns
        -------
        float
            Material poisson ratio value.
        """
        try:
            return self.get_property(GrpcMaterialProperty.POISSONS_RATIO).value
        except:
            return None

    @poisson_ratio.setter
    def poisson_ratio(self, value):
        """Set material poisson ratio."""
        self.set_property(GrpcMaterialProperty.POISSONS_RATIO, GrpcValue(value))

    @property
    def thermal_expansion_coefficient(self):
        """Material thermal coefficient.

        Returns
        -------
        float
            Material thermal coefficient value.

        """
        try:
            return self.get_property(GrpcMaterialProperty.THERMAL_EXPANSION_COEFFICIENT).value
        except:
            return None

    @thermal_expansion_coefficient.setter
    def thermal_expansion_coefficient(self, value):
        """Set material thermal coefficient."""
        self.set_property(GrpcMaterialProperty.THERMAL_EXPANSION_COEFFICIENT, GrpcValue(value))

    def set_debye_model(self):
        """Set Debye model on current material."""
        super(Material, self.__class__).dielectric_material_model.__set__(self, GrpcDebyeModel.create())

    def set_multipole_debye_model(self):
        """Set multi-pole debeye model on current material."""
        super(Material, self.__class__).dielectric_material_model.__set__(self, GrpcMultipoleDebyeModel.create())

    def set_djordjecvic_sarkar_model(self):
        """Set Djordjecvic-Sarkar model on current material."""
        super(Material, self.__class__).dielectric_material_model.__set__(self, GrpcDjordjecvicSarkarModel.create())

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
                if not self.__dielectric_model:
                    self.__dielectric_model = GrpcDjordjecvicSarkarModel.create()
                for attribute in DC_ATTRIBUTES:
                    if attribute in input_dict:
                        if attribute == "use_dc_relative_conductivity" and input_dict[attribute] is not None:
                            self.__dielectric_model.use_dc_relative_conductivity = True
                        setattr(self, attribute, input_dict[attribute])
                self.__material_def.dielectric_material_model = (
                    self.__dielectric_model
                )  # Check material is properly assigned
            # Unset DS model if it is already assigned to the material in the database
            elif self.__dielectric_model:
                self.__material_def.dielectric_material_model = None

    def __load_all_properties(self):
        """Load all properties of the material."""
        res = MaterialProperties()
        for property in res.model_dump().keys():
            value = getattr(self, property)
            setattr(res, property, value)
        return res


class Materials(object):
    """Manages EDB methods for material management accessible from `Edb.materials` property."""

    def __init__(self, edb: Edb):
        self.__edb = edb
        self.__syslib = os.path.join(self.__edb.base_path, "syslib")

    def __contains__(self, item):
        if isinstance(item, Material):
            return item.name in self.materials
        else:
            return item in self.materials

    def __getitem__(self, item):
        return self.materials[item]

    @property
    def syslib(self):
        """Get the project sys library.

        Returns
        -------
        str
            Syslib path.
        """
        return self.__syslib

    @property
    def materials(self):
        """Get materials.

        Returns
        -------
        Dict[str, :class:`Material <pyedb.grpc.database.definition.materials.Material>`]
            Materials dictionary.
        """
        materials = {
            material_def.name: Material(self.__edb, material_def) for material_def in self.__edb.active_db.material_defs
        }
        return materials

    def add_material(self, name: str, **kwargs):
        """Add a new material.

        Parameters
        ----------
        name : str
            Material name.

        Returns
        -------
        :class:`Material <pyedb.grpc.database.definition.materials.Material>`
            Material object.
        """
        curr_materials = self.materials
        if name in curr_materials:
            raise ValueError(f"Material {name} already exists in material library.")
        elif name.lower() in (material.lower() for material in curr_materials):
            m = {material.lower(): material for material in curr_materials}[name.lower()]
            raise ValueError(f"Material names are case-insensitive and '{name}' already exists as '{m}'.")

        material_def = GrpcMaterialDef.create(self.__edb.active_db, name)
        material = Material(self.__edb, material_def)
        # Apply default values to the material
        if "permeability" not in kwargs:
            kwargs["permeability"] = PERMEABILITY_DEFAULT_VALUE
        attributes_input_dict = {key: val for (key, val) in kwargs.items() if key in ATTRIBUTES + DC_ATTRIBUTES}
        if "loss_tangent" in kwargs:  # pragma: no cover
            warnings.warn(
                "This key is deprecated in versions >0.7.0 and will soon be removed. "
                "Use key dielectric_loss_tangent instead.",
                DeprecationWarning,
            )
            attributes_input_dict["dielectric_loss_tangent"] = kwargs["loss_tangent"]
        if attributes_input_dict:
            material.update(attributes_input_dict)

        return material

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
        :class:`Material <pyedb.grpc.database.definition.materials.Material>`
            Material object.

        """
        extended_kwargs = {key: value for (key, value) in kwargs.items()}
        extended_kwargs["conductivity"] = conductivity
        material = self.add_material(name, **extended_kwargs)

        return material

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
        :class:`Material <pyedb.grpc.database.definition.materials.Material>`
            Material object.
        """
        extended_kwargs = {key: value for (key, value) in kwargs.items()}
        extended_kwargs["permittivity"] = permittivity
        extended_kwargs["dielectric_loss_tangent"] = dielectric_loss_tangent
        material = self.add_material(name, **extended_kwargs)

        return material

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
        :class:`Material <pyedb.grpc.database.definition.materials.Material>`
            Material object.
        """
        curr_materials = self.materials
        if name in curr_materials:
            raise ValueError(f"Material {name} already exists in material library.")
        elif name.lower() in (material.lower() for material in curr_materials):
            raise ValueError(f"Material names are case-insensitive and {name.lower()} already exists.")

        material_model = GrpcDjordjecvicSarkarModel.create()
        material_model.relative_permitivity_at_frequency = permittivity_at_frequency
        material_model.loss_tangent_at_frequency = loss_tangent_at_frequency
        material_model.frequency = dielectric_model_frequency
        if dc_conductivity is not None:
            material_model.dc_conductivity = dc_conductivity
            material_model.use_dc_relative_conductivity = True
        if dc_permittivity is not None:
            material_model.dc_relative_permitivity = dc_permittivity
        try:
            material = self.__add_dielectric_material_model(name, material_model)
            for key, value in kwargs.items():
                setattr(material, key, value)
            if "loss_tangent" in kwargs:  # pragma: no cover
                warnings.warn(
                    "This key is deprecated in versions >0.7.0 and will soon be removed. "
                    "Use key dielectric_loss_tangent instead.",
                    DeprecationWarning,
                )
                setattr(material, "dielectric_loss_tangent", kwargs["loss_tangent"])
            return material
        except MaterialModelException:
            raise ValueError("Use realistic values to define DS model.")

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
        :class:`Material <pyedb.grpc.database.definition.materials.Material>`
            Material object.
        """
        curr_materials = self.materials
        if name in curr_materials:
            raise ValueError(f"Material {name} already exists in material library.")
        elif name.lower() in (material.lower() for material in curr_materials):
            raise ValueError(f"Material names are case-insensitive and {name.lower()} already exists.")
        material_model = GrpcDebyeModel.create()
        material_model.frequency_range = (lower_freqency, higher_frequency)
        material_model.loss_tangent_at_high_low_frequency = (loss_tangent_low, loss_tangent_high)
        material_model.relative_permitivity_at_high_low_frequency = (permittivity_low, permittivity_high)
        try:
            material = self.__add_dielectric_material_model(name, material_model)
            for key, value in kwargs.items():
                setattr(material, key, value)
            if "loss_tangent" in kwargs:  # pragma: no cover
                warnings.warn(
                    "This key is deprecated in versions >0.7.0 and will soon be removed. "
                    "Use key dielectric_loss_tangent instead.",
                    DeprecationWarning,
                )
                setattr(material, "dielectric_loss_tangent", kwargs["loss_tangent"])
            return material
        except MaterialModelException:
            raise ValueError("Use realistic values to define Debye model.")

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
        :class:`Material <pyedb.grpc.database.definition.materials.Material>`
            Material object.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb()
        >>> freq = [0, 2, 3, 4, 5, 6]
        >>> rel_perm = [1e9, 1.1e9, 1.2e9, 1.3e9, 1.5e9, 1.6e9]
        >>> loss_tan = [0.025, 0.026, 0.027, 0.028, 0.029, 0.030]
        >>> diel = edb.materials.add_multipole_debye_material("My_MP_Debye", freq, rel_perm, loss_tan)
        """
        curr_materials = self.materials
        if name in curr_materials:
            raise ValueError(f"Material {name} already exists in material library.")
        elif name.lower() in (material.lower() for material in curr_materials):
            raise ValueError(f"Material names are case-insensitive and {name.lower()} already exists.")

        frequencies = [float(i) for i in frequencies]
        permittivities = [float(i) for i in permittivities]
        loss_tangents = [float(i) for i in loss_tangents]
        material_model = GrpcMultipoleDebyeModel.create()
        material_model.set_parameters(frequencies, permittivities, loss_tangents)
        try:
            material = self.__add_dielectric_material_model(name, material_model)
            for key, value in kwargs.items():
                setattr(material, key, value)
            if "loss_tangent" in kwargs:  # pragma: no cover
                warnings.warn(
                    "This key is deprecated in versions >0.7.0 and will soon be removed. "
                    "Use key dielectric_loss_tangent instead.",
                    DeprecationWarning,
                )
                setattr(material, "dielectric_loss_tangent", kwargs["loss_tangent"])
            return material
        except MaterialModelException:
            raise ValueError("Use realistic values to define Multipole Debye model.")

    def __add_dielectric_material_model(self, name, material_model):
        """Add a dielectric material model.

        Parameters
        ----------
        name : str
            Name of the dielectric.
        material_model : Any
            Dielectric material model.
        """
        if GrpcMaterialDef.find_by_name(self.__edb.active_db, name).is_null:
            if name.lower() in (material.lower() for material in self.materials):
                raise ValueError(f"Material names are case-insensitive and {name.lower()} already exists.")
            GrpcMaterialDef.create(self.__edb.active_db, name)

        material_def = GrpcMaterialDef.find_by_name(self.__edb.active_db, name)
        material_def.dielectric_material_model = material_model
        material = Material(self.__edb, material_def)
        return material

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
        :class:`Material <pyedb.grpc.database.definition.materials.Material>`
            Material object.
        """
        curr_materials = self.materials
        if new_material_name in curr_materials:
            raise ValueError(f"Material {new_material_name} already exists in material library.")
        elif new_material_name.lower() in (material.lower() for material in curr_materials):
            raise ValueError(f"Material names are case-insensitive and {new_material_name.lower()} already exists.")

        material = self.materials[material_name]
        material_def = GrpcMaterialDef.create(self.__edb.active_db, new_material_name)
        material_dict = material.to_dict()
        new_material = Material(self.__edb, material_def)
        new_material.update(material_dict)
        return new_material

    def delete_material(self, material_name):
        """

        .deprecated: pyedb 0.32.0 use `delete` instead.

        Parameters
        ----------
        material_name : str
            Name of the material to delete.

        """
        warnings.warn(
            "`delete_material` is deprecated use `delete` instead.",
            DeprecationWarning,
        )
        self.delete(material_name)

    def delete(self, material_name):
        """Remove a material from the database.

        Returns
        -------
        bool

        """
        material_def = GrpcMaterialDef.find_by_name(self.__edb.active_db, material_name)
        if material_def.is_null:
            raise ValueError(f"Cannot find material {material_name}.")
            return False
        material_def.delete()
        return True

    def update_material(self, material_name, input_dict):
        """Update material attributes."""
        if material_name not in self.materials:
            raise ValueError(f"Material {material_name} does not exist in material library.")

        material = self[material_name]
        attributes_input_dict = {key: val for (key, val) in input_dict.items() if key in ATTRIBUTES + DC_ATTRIBUTES}
        if "loss_tangent" in input_dict:  # pragma: no cover
            warnings.warn(
                "This key is deprecated in versions >0.7.0 and will soon be removed. "
                "Use key dielectric_loss_tangent instead.",
                DeprecationWarning,
            )
            attributes_input_dict["dielectric_loss_tangent"] = input_dict["loss_tangent"]
        if attributes_input_dict:
            material.update(attributes_input_dict)
        return material

    def load_material(self, material: dict):
        """Load material."""
        if material:
            material_name = material["name"]
            material_conductivity = material.get("conductivity", None)
            if material_conductivity and material_conductivity > 1e4:
                self.add_conductor_material(material_name, material_conductivity)
            else:
                material_permittivity = material["permittivity"]
                if "loss_tangent" in material:  # pragma: no cover
                    warnings.warn(
                        "This key is deprecated in versions >0.7.0 and will soon be removed. "
                        "Use key dielectric_loss_tangent instead.",
                        DeprecationWarning,
                    )
                    material_dlt = material["loss_tangent"]
                else:
                    material_dlt = material["dielectric_loss_tangent"]
                self.add_dielectric_material(material_name, material_permittivity, material_dlt)

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
        # material_property_id = GrpcMaterialProperty.CONDUCTIVITY self.__edb_definition.MaterialPropertyId
        property_name_to_id = {
            "Permittivity": GrpcMaterialProperty.PERMITTIVITY,
            "Permeability": GrpcMaterialProperty.PERMEABILITY,
            "Conductivity": GrpcMaterialProperty.CONDUCTIVITY,
            "DielectricLossTangent": GrpcMaterialProperty.DIELECTRIC_LOSS_TANGENT,
            "MagneticLossTangent": GrpcMaterialProperty.MAGNETIC_LOSS_TANGENT,
            "ThermalConductivity": GrpcMaterialProperty.THERMAL_CONDUCTIVITY,
            "MassDensity": GrpcMaterialProperty.MASS_DENSITY,
            "SpecificHeat": GrpcMaterialProperty.SPECIFIC_HEAT,
            "YoungsModulus": GrpcMaterialProperty.YOUNGS_MODULUS,
            "PoissonsRatio": GrpcMaterialProperty.POISSONS_RATIO,
            "ThermalExpansionCoefficient": GrpcMaterialProperty.THERMAL_EXPANSION_COEFFICIENT,
            "InvalidProperty": GrpcMaterialProperty.INVALID_PROPERTY,
        }

        if property_name == "loss_tangent":
            warnings.warn(
                "This key is deprecated in versions >0.7.0 and will soon be removed. "
                "Use key dielectric_loss_tangent instead.",
                DeprecationWarning,
            )
            property_name = "dielectric_loss_tangent"
        match = difflib.get_close_matches(property_name, property_name_to_id, 1, 0.7)
        if match:
            return property_name_to_id[match[0]]
        else:
            return property_name_to_id["InvalidProperty"]

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
                elif "loss_tangent" in material_properties:  # pragma: no cover
                    warnings.warn(
                        "This key is deprecated in versions >0.7.0 and will soon be removed. "
                        "Use key dielectric_loss_tangent instead.",
                        DeprecationWarning,
                    )
                    material_properties["dielectric_loss_tangent"] = material_properties["loss_tangent"]
                    del material_properties["loss_tangent"]
                self.add_material(material_name, **material_properties)
            else:
                self.__edb.logger.warning(f"Material {material_name} already exist and was not loaded from AMAT file.")
        return True

    def iterate_materials_in_amat(self, amat_file=None):
        """Iterate over material description in an AMAT file.

        Parameters
        ----------
        amat_file : str
            Full path to the AMAT file to read.

        Yields
        ------
        dict
        """
        if amat_file is None:
            amat_file = os.path.join(self.__edb.base_path, "syslib", "Materials.amat")

        begin_regex = re.compile(r"^\$begin '(.+)'")
        end_regex = re.compile(r"^\$end '(.+)'")
        material_properties = ATTRIBUTES.copy()
        # Remove cases manually handled
        material_properties.remove("conductivity")

        with open(amat_file, "r") as amat_fh:
            in_material_def = False
            material_description = {}
            for line in amat_fh:
                if in_material_def:
                    # Yield material definition
                    if end_regex.search(line):
                        in_material_def = False
                        yield material_description
                        material_description = {}
                    # Extend material definition if possible
                    else:
                        for material_property in material_properties:
                            if material_property in line:
                                value = get_line_float_value(line)
                                if value is not None:
                                    material_description[material_property] = value
                                break
                        # Extra case to cover bug in syslib AMAT file (see #364)
                        if "thermal_expansion_coeffcient" in line:
                            value = get_line_float_value(line)
                            if value is not None:
                                material_description["thermal_expansion_coefficient"] = value
                        # Extra case to avoid confusion ("conductivity" is included in "thermal_conductivity")
                        if "conductivity" in line and "thermal_conductivity" not in line:
                            value = get_line_float_value(line)
                            if value is not None:
                                material_description["conductivity"] = value
                        # Extra case to avoid confusion ("conductivity" is included in "thermal_conductivity")
                        if (
                            "loss_tangent" in line
                            and "dielectric_loss_tangent" not in line
                            and "magnetic_loss_tangent" not in line
                        ):
                            warnings.warn(
                                "This key is deprecated in versions >0.7.0 and will soon be removed. "
                                "Use key dielectric_loss_tangent instead.",
                                DeprecationWarning,
                            )
                            value = get_line_float_value(line)
                            if value is not None:
                                material_description["dielectric_loss_tangent"] = value
                # Check if we reach the beginning of a material description
                else:
                    match = begin_regex.search(line)
                    if match:
                        material_name = match.group(1)
                        # Skip unwanted data
                        if material_name in ("$index$", "$base_index$"):
                            continue
                        material_description["name"] = match.group(1)
                        in_material_def = True

    def read_materials(self, amat_file):
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
        res = {}
        for material in self.iterate_materials_in_amat(amat_file):
            material_name = material["name"]
            res[material_name] = {}
            for material_property, value in material.items():
                if material_property != "name":
                    res[material_name][material_property] = value

        return res

    def read_syslib_material(self, material_name):
        """Read a specific material from syslib AMAT file.

        Parameters
        ----------
        material_name : str
            Name of the material.

        Returns
        -------
        dict
            {material name: dict of material properties}.
        """
        res = {}
        amat_file = os.path.join(self.__edb.base_path, "syslib", "Materials.amat")
        for material in self.iterate_materials_in_amat(amat_file):
            iter_material_name = material["name"]
            if iter_material_name == material_name or iter_material_name.lower() == material_name.lower():
                for material_property, value in material.items():
                    if material_property != "name":
                        res[material_property] = value
                return res

        self.__edb.logger.error(f"Material {material_name} does not exist in syslib AMAT file.")
        return res
