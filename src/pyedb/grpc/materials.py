from __future__ import absolute_import  # noreorder

import difflib
import logging
import warnings


from pyedb.generic.general_methods import pyedb_function_handler
from ansys.edb.definition.material_def import MaterialProperty, MaterialDef
from ansys.edb.utility.value import Value
from ansys.edb.definition.material_def import MaterialDef
from ansys.edb.definition.djordjecvic_sarkar_model import DjordjecvicSarkarModel
from ansys.edb.definition.multipole_debye_model import MultipoleDebyeModel
from ansys.edb.definition.debye_model import DebyeModel
logger = logging.getLogger(__name__)


class Material(object):
    """Manages EDB methods for material property management."""

    def __init__(self, pclass, edb_material_def):
        self._pclass = pclass
        self._name = edb_material_def.GetName()
        self._edb_material_def = edb_material_def
        self._conductivity = 0.0
        self._loss_tangent = 0.0
        self._magnetic_loss_tangent = 0.0
        self._mass_density = 0.0
        self._permittivity = 0.0
        self._permeability = 0.0
        self._poisson_ratio = 0.0
        self._specific_heat = 0.0
        self._thermal_conductivity = 0.0
        self._youngs_modulus = 0.0
        self._thermal_expansion_coefficient = 0.0
        self._dc_conductivity = 0.0
        self._dc_permittivity = 0.0
        self._dielectric_model_frequency = 0.0
        self._loss_tangent_at_frequency = 0.0
        self._permittivity_at_frequency = 0.0


    @property
    def name(self):
        """Retrieve material name."""
        return self._name

    @property
    def _db(self):
        return self._pclass._db

    @property
    def _edb(self):
        return self._pclass._edb

    @pyedb_function_handler()
    def _get_property(self, property_name):
        _, property_box = self._edb_material_def.property(property_name)
        if isinstance(property_box, float):
            return property_box
        else:
            return property_box.value

    @property
    def conductivity(self):
        self._conductivity = self._get_property(MaterialProperty.CONDUCTIVITY)
        return self._conductivity

    @conductivity.setter
    def conductivity(self, value):
        """Retrieve material conductivity."""
        self._edb_material_def.property(MaterialProperty.CONDUCTIVITY, Value(value))
        self._conductivity = value

    @property
    def permittivity(self):
        """Retrieve material permittivity."""
        self._permittivity = self._get_property(MaterialProperty.PERMITTIVITY)
        return self._permittivity

    @permittivity.setter
    def permittivity(self, value):
        self._edb_material_def.set_property(MaterialProperty.PERMITTIVITY, Value(value))
        self._permittivity = value

    @property
    def permeability(self):
        """Retrieve material permeability."""
        material_id = self._edb.definition.MaterialPropertyId.Permeability
        self._permeability = self._get_property(material_id)
        return self._permeability

    @permeability.setter
    def permeability(self, value):
        self._edb_material_def.set_property(MaterialProperty.PERMEABILITY, Value(value))
        self._permeability = value

    @property
    def loss_tangent(self):
        """Retrieve material loss tangent."""
        self._loss_tangent = self._get_property(MaterialProperty.DIELECTRIC_LOSS_TANGENT)
        return self._loss_tangent

    @loss_tangent.setter
    def loss_tangent(self, value):
        self._edb_material_def.set_property(MaterialProperty.DIELECTRIC_LOSS_TANGENT, Value(value))
        self._loss_tangent = value

    @property
    def dc_conductivity(self):
        """"""
        if self._edb_material_def.dielectric_material_model:
            return self._edb_material_def.dielectric_material_model.dc_conductivity

    @dc_conductivity.setter
    def dc_conductivity(self, value):
        if self._edb_material_def.dielectric_material_model:
            self._edb_material_def.dielectric_material_model.dc_conductivity = Value(value)

    @property
    def dc_permittivity(self):
        """"""
        if self._edb_material_def.dielectric_material_model:
            return self._edb_material_def.dielectric_material_model.dc_relative_permitivity

    @dc_permittivity.setter
    def dc_permittivity(self, value):
        if self._edb_material_def.dielectric_material_model:
            self._edb_material_def.dielectric_material_model.dc_relative_permitivity = Value(value)

    @property
    def dielectric_model_frequency(self):
        """

        Returns
        -------
        Frequency in GHz
        """
        if self._edb_material_def.dielectric_material_model:
            return self._edb_material_def.dielectric_material_model.frequency

    @dielectric_model_frequency.setter
    def dielectric_model_frequency(self, value):
        if self._edb_material_def.dielectric_material_model:
            self._edb_material_def.dielectric_material_model.frequency = Value(value)

    @property
    def loss_tangent_at_frequency(self):
        if self._edb_material_def.dielectric_material_model:
            return self._edb_material_def.dielectric_material_model.loss_tangent_at_frequency

    @loss_tangent_at_frequency.setter
    def loss_tangent_at_frequency(self, value):
        if self._edb_material_def.dielectric_material_model:
            self._edb_material_def.dielectric_material_model.loss_tangent_at_frequency = Value(value)

    @property
    def permittivity_at_frequency(self):
        if self._edb_material_def.dielectric_material_model:
            return self._edb_material_def.dielectric_material_model.relative_permitivity_at_frequency

    @permittivity_at_frequency.setter
    def permittivity_at_frequency(self, value):
        if self._edb_material_def.dielectric_material_model:
            self._edb_material_def.dielectric_material_model.relative_permitivity_at_frequency = Value(value)

    @property
    def magnetic_loss_tangent(self):
        """Retrieve material magnetic loss tangent."""
        self._magnetic_loss_tangent = self._get_property(MaterialProperty.MAGNETIC_LOSS_TANGENT)
        return self._magnetic_loss_tangent

    @magnetic_loss_tangent.setter
    def magnetic_loss_tangent(self, value):
        self._edb_material_def.set_property(MaterialProperty.MAGNETIC_LOSS_TANGENT, Value(value))
        self._magnetic_loss_tangent = value

    @property
    def thermal_conductivity(self):
        """Retrieve material thermal conductivity."""
        self._thermal_conductivity = self._get_property(MaterialProperty.THERMAL_CONDUCTIVITY)
        return self._thermal_conductivity

    @thermal_conductivity.setter
    def thermal_conductivity(self, value):
        self._edb_material_def.set_property(MaterialProperty.THERMAL_CONDUCTIVITY, Value(value))
        self._thermal_conductivity = value

    @property
    def mass_density(self):
        """Retrieve material mass density."""
        self._mass_density = self._get_property(MaterialProperty.MASS_DENSITY)
        return self._mass_density

    @mass_density.setter
    def mass_density(self, value):
        self._edb_material_def.set_property(MaterialProperty.MASS_DENSITY, Value(value))
        self._mass_density = value

    @property
    def youngs_modulus(self):
        """Retrieve material Young's Modulus."""
        self._youngs_modulus = self._get_property(MaterialProperty.YOUNGS_MODULUS)
        return self._youngs_modulus

    @youngs_modulus.setter
    def youngs_modulus(self, value):
        self._edb_material_def.set_property(MaterialProperty.YOUNGS_MODULUS, Value(value))
        self._youngs_modulus = value

    @property
    def specific_heat(self):
        """Retrieve material Specific Heat."""
        material_id = MaterialProperty.SPECIFIC_HEAT
        self._specific_heat = self._get_property(material_id)
        return self._specific_heat

    @specific_heat.setter
    def specific_heat(self, value):
        self._edb_material_def.set_property(MaterialProperty.SPECIFIC_HEAT, Value(value))
        self._specific_heat = value

    @property
    def poisson_ratio(self):
        """Retrieve material Poisson Ratio."""
        self._poisson_ratio = self._get_property(MaterialProperty.POISSONS_RATIO)
        return self._poisson_ratio

    @poisson_ratio.setter
    def poisson_ratio(self, value):
        self._edb_material_def.set_property(MaterialProperty.POISSONS_RATIO, Value(value))
        self._poisson_ratio = value

    @property
    def thermal_expansion_coefficient(self):
        """Retrieve material Thermal Coefficient.."""
        self._thermal_expansion_coefficient = self._get_property(MaterialProperty.THERMAL_EXPANSION_COEFFICIENT)
        return self._thermal_expansion_coefficient

    @thermal_expansion_coefficient.setter
    def thermal_expansion_coefficient(self, value):
        self._edb_material_def.set_property(MaterialProperty.THERMAL_EXPANSION_COEFFICIENT, Value(value))
        self._thermal_expansion_coefficient = value

    @pyedb_function_handler()
    def _json_format(self):
        out_dict = {}
        if self.permittivity == 0:  # pragma no cover
            self.permittivity = 1.0
        if self.permeability == 0:  # pragma no cover
            self.permeability = 1.0
        self._name = self.name
        self._conductivity = self.conductivity
        self._loss_tangent = self.loss_tangent
        self._magnetic_loss_tangent = self.magnetic_loss_tangent
        self._mass_density = self.mass_density
        self._permittivity = self.permittivity
        self._permeability = self.permeability
        self._poisson_ratio = self.poisson_ratio
        self._specific_heat = self.specific_heat
        self._thermal_conductivity = self.thermal_conductivity
        self._youngs_modulus = self.youngs_modulus
        self._thermal_expansion_coefficient = self.thermal_expansion_coefficient
        self._dc_conductivity = self.dc_conductivity
        self._dc_permittivity = self.dc_permittivity
        self._dielectric_model_frequency = self.dielectric_model_frequency
        self._loss_tangent_at_frequency = self.loss_tangent_at_frequency
        self._permittivity_at_frequency = self.permittivity_at_frequency
        for k, v in self.__dict__.items():
            if not k == "_pclass" and not k == "_edb_material_def":
                out_dict[k[1:]] = v
        return out_dict

    @pyedb_function_handler()
    def _load(self, input_dict):
        if input_dict:
            self.conductivity = input_dict["conductivity"]
            self.loss_tangent = input_dict["loss_tangent"]
            self.magnetic_loss_tangent = input_dict["magnetic_loss_tangent"]
            self.mass_density = input_dict["mass_density"]
            self.permittivity = input_dict["permittivity"]
            self.permeability = input_dict["permeability"]
            self.poisson_ratio = input_dict["poisson_ratio"]
            self.specific_heat = input_dict["specific_heat"]
            self.thermal_conductivity = input_dict["thermal_conductivity"]
            self.youngs_modulus = input_dict["youngs_modulus"]
            self.thermal_expansion_coefficient = input_dict["thermal_expansion_coefficient"]
            if input_dict["dielectric_model_frequency"] is not None:
                if self._edb_material_def.dielectric_material_model:
                    model = self._edb_material_def.dielectric_material_model
                    self.dielectric_model_frequency = input_dict["dielectric_model_frequency"]
                    self.loss_tangent_at_frequency = input_dict["loss_tangent_at_frequency"]
                    self.permittivity_at_frequency = input_dict["permittivity_at_frequency"]
                    if input_dict["dc_permittivity"] is not None:
                        model.use_dc_relative_permitivity = True
                        self.dc_permittivity = input_dict["dc_permittivity"]
                    self.dc_conductivity = input_dict["dc_conductivity"]
                else:
                    if not self._pclass.add_djordjevicsarkar_material(
                        input_dict["name"],
                        input_dict["permittivity_at_frequency"],
                        input_dict["loss_tangent_at_frequency"],
                        input_dict["dielectric_model_frequency"],
                        input_dict["dc_permittivity"],
                        input_dict["dc_conductivity"],
                    ):
                        self._pclass._pedb.logger.warning(
                            'Cannot set DS model for material "{}". Check for realistic '
                            "values that define DS Model".format(input_dict["name"])
                        )
            else:
                # To unset DS model if already assigned to the material in database
                if self._edb_material_def.dielectric_material_model:
                    self._edb_material_def.dielectric_material_model = Value(None)


class Materials(object):
    """Manages EDB methods for material management accessible from `Edb.materials` property."""

    def __getitem__(self, item):
        return self.materials[item]

    def __init__(self, pedb):
        self._pedb = pedb
        if not self.materials:
            self.add_material("air")
            self.add_material("copper", 1, 0.999991, 5.8e7, 0, 0)
            self.add_material("fr4_epoxy", 4.4, 1, 0, 0.02, 0)
            self.add_material("solder_mask", 3.1, 1, 0, 0.035, 0)

    @pyedb_function_handler()
    def _edb_value(self, value):
        return self._pedb.edb_value(value)

    @property
    def _edb(self):
        return self._pedb

    @property
    def _db(self):
        return self._pedb.active_db

    @property
    def materials(self):
        """Retrieve dictionary of material from material library."""
        return {obj.name: Material(self, obj) for obj in list(self._db.material_defs)}

    @pyedb_function_handler()
    def add_material(
        self,
        name="air",
        permittivity=1.0006,
        permeability=1.0000004,
        conductivity=0,
        dielectric_loss_tangent=0,
        magnetic_loss_tangent=0,
    ):
        """Add a new material.

        Parameters
        ----------
        name : str, optional
            Material Name. The default is ``"air"``.
        permittivity : float, str, optional
            Material permittivity. The default is ``1.0006``.
        permeability : float, str, optional
            Material permeability. The default is ``1.0000004``.
        conductivity : float, str, optional
            Material conductivity. The default is ``0``.
        dielectric_loss_tangent : float, str, optional
            Material dielectric loss tangent. The default is ``0``.
        magnetic_loss_tangent : float, str, optional
            Material magnetic loss tangent. The default is ``0``.

        Returns
        -------
        :class:`pyaedt.edb_core.materials.Material`
        """
        if not name in self.materials:
            MaterialDef.create(self._db, name)
            new_material = self.materials[name]
            new_material.permittivity = permittivity
            new_material.permeability = permeability
            new_material.conductivity = conductivity
            new_material.loss_tangent = dielectric_loss_tangent
            new_material.magnetic_loss_tangent = magnetic_loss_tangent
            return new_material
        else:  # pragma: no cover
            warnings.warn("Material {} already exists in material library.".format(name))
            return False

    @pyedb_function_handler()
    def add_conductor_material(self, name, conductivity):
        """Add a new conductor material in library.

        Parameters
        ----------
        name : str
            Name of the new material.
        conductivity : float
            Conductivity of the new material.

        Returns
        -------
        :class:`pyaedt.edb_core.materials.Material`

        """
        if not name in self.materials:
            MaterialDef.create(self._db, name)
            new_material = self.materials[name]
            new_material.conductivity = conductivity
            new_material.permittivity = 1
            new_material.permeability = 1
            return new_material
        else:  # pragma: no cover
            warnings.warn("Material {} already exists in material library.".format(name))
            return False

    @pyedb_function_handler()
    def add_dielectric_material(self, name, permittivity, loss_tangent, permeability=1):
        """Add a new dielectric material in library.

        Parameters
        ----------
        name : str
            Name of the new material.
        permittivity : float
            Permittivity of the new material.
        loss_tangent : float
            Loss tangent of the new material.
        permeability : float
            Permeability of the new material.

        Returns
        -------
        :class:`pyaedt.edb_core.materials.Material`
        """
        if not name in self.materials:
            MaterialDef.create(self._db, name)
            new_material = self.materials[name]
            new_material.permittivity = permittivity
            new_material.loss_tangent = loss_tangent
            new_material.permeability = permeability
            return new_material
        else:
            warnings.warn("Material {} already exists in material library.".format(name))
            return False

    @pyedb_function_handler()
    def get_djordjevicsarkar_model(self, material_name=None):
        """Djordjevic-Sarkar model if present.

        Parameters
        ----------
        material_name : str

        Returns
        -------

        """
        material = self.materials[material_name]
        if material:
            return material.dielectric_material_model()

    @pyedb_function_handler()
    def add_djordjevicsarkar_material(
        self, name, permittivity, loss_tangent, test_frequency, dc_permittivity=None, dc_conductivity=None
    ):
        """Create a Djordjevic_Sarkar dielectric.

        Parameters
        ----------
        name : str
            Name of the dielectric.
        permittivity : float
            Relative permittivity of the dielectric.
        loss_tangent : float
            Loss tangent for the material.
        test_frequency : float
            Test frequency in GHz for the dielectric.
        dc_permittivity : float, optional
            DC Relative permittivity of the dielectric.
        dc_conductivity : float, optional
            DC Conductivity of the dielectric.

        Returns
        -------
        :class:`pyaedt.edb_core.materials.Material`
            Material definition.
        """
        material_def = DjordjecvicSarkarModel()
        material_def.frequency = test_frequency
        material_def.loss_tangent_at_frequency = Value(loss_tangent)
        material_def.relative_permitivity_at_frequency = permittivity
        if dc_conductivity is not None:
            material_def.dc_conductivity = dc_conductivity
        if dc_permittivity is not None:
            material_def.use_dc_relative_conductivity = True
            material_def.dc_relative_permitivity = dc_permittivity
        return self._add_dielectric_material_model(name, material_def)

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
    ):
        """Create a dielectric with the Debye model.

        Parameters
        ----------
        name : str
            Name of the dielectric.
        permittivity_low : float
            Relative permittivity of the dielectric at the frequency specified
            for ``lower_frequency``.
        permittivity_high : float
            Relative permittivity of the dielectric at the frequency specified
            for ``higher_frequency``.
        loss_tangent_low : float
            Loss tangent for the material at the frequency specified
            for ``lower_frequency``.
        loss_tangent_high : float
            Loss tangent for the material at the frequency specified
            for ``higher_frequency``.
        lower_freqency : float
            Value for the lower frequency.
        higher_frequency : float
            Value for the higher frequency.

        Returns
        -------
        :class:`pyaedt.edb_core.materials.Material`
            Material definition.
        """
        material_def = DebyeModel()
        material_def.frequency_range = (lower_freqency, higher_frequency)
        material_def.loss_tangent_at_high_low_frequency = (loss_tangent_low, loss_tangent_high)
        material_def.relative_permitivity_at_high_low_frequency = (Value(permittivity_low), Value(permittivity_high)
        )
        return self._add_dielectric_material_model(name, material_def)

    @pyedb_function_handler()
    def add_multipole_debye_material(
        self,
        name,
        frequencies,
        permittivities,
        loss_tangents,
    ):
        """Create a dielectric with the Multipole Debye model.

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
        :class:`pyaedt.edb_core.materials.Material`
            Material definition.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb()
        >>> freq = [0, 2, 3, 4, 5, 6]
        >>> rel_perm = [1e9, 1.1e9, 1.2e9, 1.3e9, 1.5e9, 1.6e9]
        >>> loss_tan = [0.025, 0.026, 0.027, 0.028, 0.029, 0.030]
        >>> diel = edb.materials.add_multipole_debye_material("My_MP_Debye", freq, rel_perm, loss_tan)
        """
        frequencies = [float(i) for i in frequencies]
        permittivities = [float(i) for i in permittivities]
        loss_tangents = [float(i) for i in loss_tangents]
        material_def = MultipoleDebyeModel()
        material_def.set_parameters(frequencies, permittivities, loss_tangents)
        return self._add_dielectric_material_model(name, material_def)

    @pyedb_function_handler()
    def _add_dielectric_material_model(self, name, material_model):
        if MaterialDef.find_by_name(self._db, name).is_null:
            MaterialDef.create(self._db, name)
        material_def = MaterialDef.find_by_name(self._db, name)
        if material_def:
            material_def.dielectric_material_model = material_model
            return material_def
        return False

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
        EDB material : class: 'Ansys.Ansoft.Edb.definition.MaterialDef'


        Examples
        --------

        >>> from pyedb import Edb
        >>> edb_app = Edb()
        >>> my_material = edb_app.materials.duplicate("copper", "my_new_copper")

        """
        material_list = {i.lower(): i for i in list(self.materials.keys())}
        if material_name.lower() in material_list and new_material_name not in self.materials:
            material_name = material_list[material_name.lower()]
            permittivity = Value(self.materials[material_name].permittivity)
            permeability = Value(self.materials[material_name].permeability)
            conductivity = Value(self.materials[material_name].conductivity)
            dielectric_loss_tangent = Value(self.materials[material_name].loss_tangent)
            magnetic_loss_tangent = Value(self.materials[material_name].magnetic_loss_tangent)
            thermal_conductivity = Value(self.materials[material_name].thermal_conductivity)
            thermal_expansion_coefficient = Value(self.materials[material_name].thermal_expansion_coefficient)
            youngs_modulus = Value(self.materials[material_name].youngs_modulus)
            poisson_ratio = Value(self.materials[material_name].poisson_ratio)
            mass_density = Value(self.materials[material_name].mass_density)
            material_model = self.materials[material_name]._edb_material_def.dielectric_material_model
            edb_material = MaterialDef.create(self._db, new_material_name)
            edb_material.set_property(MaterialProperty.PERMITTIVITY, permittivity)
            edb_material.set_property(MaterialProperty.PERMEABILITY, permeability)
            edb_material.set_property(MaterialProperty.CONDUCTIVITY, conductivity)
            edb_material.set_property(MaterialProperty.DIELECTRIC_LOSS_TANGENT, dielectric_loss_tangent)
            edb_material.set_property(MaterialProperty.THERMAL_CONDUCTIVITY, thermal_conductivity)
            edb_material.set_property(MaterialProperty.THERMAL_EXPANSION_COEFFICIENT, thermal_expansion_coefficient)
            edb_material.set_property(MaterialProperty.MASS_DENSITY, mass_density)
            edb_material.set_property(MaterialProperty.YOUNGS_MODULUS, youngs_modulus)
            edb_material.set_property(MaterialProperty.POISSONS_RATIO, poisson_ratio)
            edb_material.set_property(MaterialProperty.MAGNETIC_LOSS_TANGENT, magnetic_loss_tangent)
            edb_material.dielectric_material_model = material_model

            return edb_material

    @pyedb_function_handler()
    def _load_materials(self, material=None):
        if self.materials:
            mat_keys = [i.lower() for i in self.materials.keys()]
            mat_keys_case = [i for i in self.materials.keys()]
        else:
            mat_keys = []
            mat_keys_case = []

        if not material:
            return
        if material["name"].lower() not in mat_keys:
            if material["conductivity"] > 1e4:
                self.add_conductor_material(material["name"], material["conductivity"])
            else:
                self.add_dielectric_material(material["name"], material["permittivity"], material["loss_tangent"])
            self.materials[material["name"]]._load(material)
        else:
            self.materials[mat_keys_case[mat_keys.index(material["name"].lower())]]._load(material)

    @pyedb_function_handler()
    def material_name_to_id(self, property_name):
        """Convert a material property name to a material property ID.

        Parameters
        ----------
        property_name : str
            Name of the material property.

        Returns
        -------
        ID of the material property.
        """
        props = {
            "Permittivity": MaterialProperty.PERMITTIVITY,
            "Permeability": MaterialProperty.PERMEABILITY,
            "Conductivity": MaterialProperty.CONDUCTIVITY,
            "DielectricLossTangent": MaterialProperty.DIELECTRIC_LOSS_TANGENT,
            "MagneticLossTangent": MaterialProperty.MAGNETIC_LOSS_TANGENT,
            "ThermalConductivity": MaterialProperty.THERMAL_CONDUCTIVITY,
            "MassDensity": MaterialProperty.MASS_DENSITY,
            "SpecificHeat": MaterialProperty.SPECIFIC_HEAT,
            "YoungsModulus": MaterialProperty.YOUNGS_MODULUS,
            "PoissonsRatio": MaterialProperty.POISSONS_RATIO,
            "ThermalExpansionCoefficient": MaterialProperty.THERMAL_EXPANSION_COEFFICIENT,
            "InvalidProperty": MaterialProperty.INVALID_PROPERTY,
        }

        found_el = difflib.get_close_matches(property_name, list(props.keys()), 1, 0.7)
        if found_el:
            return props[found_el[0]]
        else:
            return MaterialProperty.INVALID_PROPERTY

    @pyedb_function_handler()
    def get_property_by_material_name(self, property_name, material_name):
        """Get the property of a material. If it is executed in IronPython,
         you must only use the first element of the returned tuple, which is a float.

        Parameters
        ----------
        material_name : str
            Name of the existing material.
        property_name : str
            Name of the material property.
            ``permittivity``
            ``permeability``
            ``conductivity``
            ``dielectric_loss_tangent``
            ``magnetic_loss_tangent``

        Returns
        -------
        float
            The float value of the property.


        Examples
        --------
        >>> from pyedb import Edb
        >>> edb_app = Edb()
        >>> returned_tuple = edb_app.materials.get_property_by_material_name("conductivity", "copper")
        >>> edb_value = returned_tuple[0]
        >>> float_value = returned_tuple[1]

        """
        if MaterialDef.find_by_name(self._pedb._db, material_name).is_null:
            self._pedb.logger.error("This material doesn't exists.")
        else:
            original_material = MaterialDef.find_by_name(self._pedb._db, material_name)
            property_box = original_material.get_property(self.material_name_to_id(property_name))
            return property_box.value
        return False
