# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import absolute_import

from ansys.edb.core.layer.layer import Layer as GrpcLayer
from ansys.edb.core.layer.layer import LayerType as GrpcLayerType


class Layer(GrpcLayer):
    """Manages Layer."""

    def __init__(self, pedb, edb_object=None, name="", layer_type="undefined", **kwargs):
        super().__init__(edb_object.msg)
        self._pedb = pedb
        self._name = name
        self._color = ()
        self._type = ""
        if edb_object:
            self._cloned_layer = self.clone()
        else:
            layer_type_mapping = {
                "conducting_layer": GrpcLayerType.CONDUCTING_LAYER,
                "air_lines_layer": GrpcLayerType.AIRLINES_LAYER,
                "errors_layer": GrpcLayerType.ERRORS_LAYER,
                "symbol_layer": GrpcLayerType.SYMBOL_LAYER,
                "measure_layer": GrpcLayerType.MEASURE_LAYER,
                "assembly_layer": GrpcLayerType.ASSEMBLY_LAYER,
                "silkscreen_layer": GrpcLayerType.SILKSCREEN_LAYER,
                "solder_mask_layer": GrpcLayerType.SOLDER_MASK_LAYER,
                "solder_paste_layer": GrpcLayerType.SOLDER_PASTE_LAYER,
                "glue_layer": GrpcLayerType.GLUE_LAYER,
                "wirebond_layer": GrpcLayerType.WIREBOND_LAYER,
                "user_layer": GrpcLayerType.USER_LAYER,
                "siwave_hfss_solver_regions": GrpcLayerType.SIWAVE_HFSS_SOLVER_REGIONS,
                "postprocessing_layer": GrpcLayerType.POST_PROCESSING_LAYER,
                "outline_layer": GrpcLayerType.OUTLINE_LAYER,
                "layer_types_count": GrpcLayerType.LAYER_TYPES_COUNT,
                "undefined_layer_type": GrpcLayerType.UNDEFINED_LAYER_TYPE,
            }
            if layer_type in layer_type_mapping:
                self.create(name=name, lyr_type=layer_type_mapping[layer_type])
                self.update(**kwargs)

    def update(self, **kwargs):
        for k, v in kwargs.items():
            if k in dir(self):
                self.__setattr__(k, v)
            else:
                self._pedb.logger.error(f"{k} is not a valid layer attribute")

    @property
    def properties(self):
        from ansys.edb.core.layer.stackup_layer import StackupLayer as GrpcStackupLayer

        from pyedb.grpc.database.stackup import StackupLayer

        if isinstance(self.cast(), GrpcStackupLayer):
            return StackupLayer(self._pedb, self.cast()).properties
        else:
            data = {"name": self.name, "type": self.type, "color": self.color}
            return data

    @properties.setter
    def properties(self, params):
        name = params.get("name", "")
        if name:
            self.name = name
        type = params.get("type", "")
        if type:
            self.type = type
        color = params.get("color", "")
        if color:
            self.color = color

    @property
    def type(self):
        return super().type.name.lower().split("_")[0]

    @property
    def _layer_name_mapping_reversed(self):
        return {j: i for i, j in self._layer_name_mapping.items()}
