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

"""Tests related to Edb
"""

import os

import pytest

pytestmark = [pytest.mark.system, pytest.mark.legacy]


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, legacy_edb_app, local_scratch, target_path, target_path2, target_path4):
        self.edbapp = legacy_edb_app
        self.local_scratch = local_scratch
        self.target_path = target_path
        self.target_path2 = target_path2
        self.target_path4 = target_path4

    def test_create_impedance_scan(self):
        xtalk_scan = self.edbapp.siwave.create_crosstalk_config_file(scan_type="impedance")
        for net in list(self.edbapp.nets.signal.keys()):
            xtalk_scan.impedance_scan.add_single_ended_net(
                name=net, nominal_impedance=45.0, warning_threshold=40.0, violation_threshold=30.0
            )
        xtalk_scan.file_path = os.path.join(self.local_scratch.path, "test_impedance_scan.xml")
        assert xtalk_scan.write_wml()

    def test_create_frequency_xtalk_scan(self):
        xtalk_scan = self.edbapp.siwave.create_crosstalk_config_file(scan_type="frequency_xtalk")
        for net in list(self.edbapp.nets.signal.keys()):
            xtalk_scan.frequency_xtalk_scan.add_single_ended_net(
                name=net,
                next_warning_threshold=5.0,
                next_violation_threshold=8.0,
                fext_warning_threshold_warning=8.0,
                fext_violation_threshold=10.0,
            )

        xtalk_scan.file_path = os.path.join(self.local_scratch.path, "test_impedance_scan.xml")
        assert xtalk_scan.write_wml()

    def test_create_time_xtalk_scan(self):
        xtalk_scan = self.edbapp.siwave.create_crosstalk_config_file(scan_type="time_xtalk")
        for net in list(self.edbapp.nets.signal.keys()):
            xtalk_scan.time_xtalk_scan.add_single_ended_net(
                name=net, driver_rise_time="132ps", voltage="2.4V", driver_impedance=45.0, termination_impedance=51.0
            )
        driver_pins = [pin for pin in list(self.edbapp.components["U1"].pins.values()) if "DDR4" in pin.net_name]
        receiver_pins = [pin for pin in list(self.edbapp.components["U1"].pins.values()) if pin.net_name == "GND"]
        for pin in driver_pins:
            xtalk_scan.time_xtalk_scan.add_driver_pins(
                name=pin.name, ref_des="U1", rise_time="20ps", voltage="1.2V", impedance=120.0
            )
        for pin in receiver_pins:
            xtalk_scan.time_xtalk_scan.add_receiver_pin(name=pin.name, ref_des="U1", impedance=80.0)
        # xtalk_scan.file_path = os.path.join(self.local_scratch.path, "test_impedance_scan.xml")
        xtalk_scan.file_path = r"D:\Temp\test_time_xtalk_scan.xml"
        assert xtalk_scan.write_wml()
