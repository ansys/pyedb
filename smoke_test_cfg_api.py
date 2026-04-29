import sys
sys.path.insert(0, 'src')

# NetsConfig
from pyedb.configuration.cfg_api.nets import NetsConfig
n = NetsConfig()
n.add_signal_nets(["SIG"])
n.add_reference_nets(["GND"])
assert n.signal_nets == ["SIG"]
assert n.reference_nets == ["GND"]
assert "reference_nets" not in n.to_dict()
print("NetsConfig OK")

# StackupConfig
from pyedb.configuration.cfg_api.stackup import StackupConfig, MaterialConfig, LayerConfig
s = StackupConfig()
m = s.add_material("copper", conductivity=5.8e7)
assert m.to_dict()["conductivity"] == 5.8e7
lyr = s.add_signal_layer("top", material="copper", fill_material="fr4", thickness="35um")
result = lyr.set_huray_roughness("0.1um", "2.9").set_etching(0.3)
assert result is lyr
print("StackupConfig OK")

# PadstacksConfig
from pyedb.configuration.cfg_api.padstacks import PadstacksConfig
ps = PadstacksConfig()
pdef = ps.add_definition("via_0.2", material="copper", hole_plating_thickness="25um")
inst = ps.add_instance(name="v1", net_name="GND", layer_range=["top", "bot"])
chained = inst.set_backdrill("L3", "0.25mm")
assert chained is inst
d = ps.to_dict()
assert d["definitions"][0]["material"] == "copper"
print("PadstacksConfig OK")

# PackageDefinitionsConfig explicit params
from pyedb.configuration.cfg_api.package_definitions import PackageDefinitionsConfig
pc = PackageDefinitionsConfig()
pkg = pc.add("PKG1", "BGA", apply_to_all=True, maximum_power="5W", theta_jb="10C/W", theta_jc="5C/W", height="1mm")
d = pkg.to_dict()
assert d["theta_jb"] == "10C/W"
print("PackageDefinitionsConfig OK")

# TerminalsConfig explicit params
from pyedb.configuration.cfg_api.terminals import TerminalsConfig
tc = TerminalsConfig()
t = tc.add_edge_terminal("t1", "prim", 0, 0, 50, "port", hfss_type="Gap", horizontal_extent_factor=8)
assert t.to_dict()["hfss_type"] == "Gap"
print("TerminalsConfig OK")

# CutoutConfig extent_type normalisation
from pyedb.configuration.cfg_api.operations import CutoutConfig
c = CutoutConfig(extent_type="convexhull")
assert c.to_dict()["extent_type"] == "ConvexHull"
c2 = CutoutConfig(extent_type="BOUNDINGBOX")
assert c2.to_dict()["extent_type"] == "BoundingBox"
c3 = CutoutConfig(extent_type="CONFORMAL")
assert c3.to_dict()["extent_type"] == "Conformal"
print("CutoutConfig extent_type normalisation OK")

# ModelerConfig explicit params
from pyedb.configuration.cfg_api.modeler import ModelerConfig
m = ModelerConfig()
m.add_padstack_definition("via_full", hole_plating_thickness="25um", material="copper", hole_range="upper_pad_to_lower_pad")
m.add_padstack_instance(name="v1", net_name="GND", definition="via_full", layer_range=["top", "bot"])
d = m.to_dict()
assert d["padstack_definitions"][0]["hole_range"] == "upper_pad_to_lower_pad"
assert d["padstack_instances"][0]["definition"] == "via_full"
print("ModelerConfig explicit params OK")

print("\nAll smoke tests passed!")

