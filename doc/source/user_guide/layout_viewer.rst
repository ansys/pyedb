Interactive 2D layout viewer
============================

The optional layout viewer displays copper, traces, pads, vias, and component
envelopes in a native PySide6 window using Qt RHI. Windows defaults to Direct3D 11;
Linux uses Vulkan. Its rendering design references
`Pomelo-Desktop <https://github.com/HaiwenZhang/Pomelo-Desktop>`_. Geometry remains
on the GPU during navigation and display changes.

Install and launch
------------------

.. code-block:: console

   pip install "pyedb[viewer]"
   python -m pyedb.viewer --demo
   python -m pyedb.viewer --demo --backend vulkan
   python -m pyedb.viewer path/to/board.aedb
   python -m pyedb.viewer path/to/board.aedb --layer TOP --color-by-layer
   python -m pyedb.viewer path/to/board.aedb --version 2026.1 --net GND --net VCC

The demo generates its geometry in code and requires no sample files, EDB server,
or license. Opening an AEDB requires a supported
gRPC EDB installation and license. The command-line viewer opens the database
read-only and closes its session on exit. ``--layer`` and ``--net`` can be
repeated to restrict the capture, ``--version`` selects the EDB server version and
``--exact-component-bounds`` reads exact component envelopes from EDB.

To use an existing gRPC session:

.. code-block:: python

   from pyedb import Edb

   edb = Edb("board.aedb", grpc=True, isreadonly=True)
   try:
       window = edb.view_layout()
   finally:
       edb.close()

The viewer displays a detached snapshot without modifying or closing a
caller-owned EDB session. An EDB-backed window retains a capture source until
the window closes, allowing ``window.refresh()`` to display subsequent design
changes. Use ``live=True`` to refresh automatically after supported PyEDB edits.
The displayed snapshot remains usable after the EDB session closes.

All included layers are read on every open. The full viewer window appears
first and reports loading progress in its canvas. With ``progressive=True``
(the default), copper appears before pads and components finish loading;
the progress indicator disappears only after the complete layout is prepared,
uploaded and drawn. Changing layer visibility after loading requires no EDB
reads or geometry uploads. No scene or GPU data is saved to disk.

Display and navigation
----------------------

The workspace uses a light theme and a white canvas with an optional grid.
Color by Net is enabled by default, and only the first listed layer is initially
visible. Opacity defaults to 75%. Use ``color_by_net=False`` or
``--color-by-layer`` for layer colors.

* Drag with the left, middle, or right mouse button to pan; arrow keys also pan.
* Scroll to zoom around the pointer, or use ``+`` and ``-`` on the canvas.
* Use the floating navigation capsule to fit or zoom.
  ``F`` / ``Home`` fits the layout, and ``B`` flips the view when the canvas has focus.
* Use the left Layers panel checkboxes or Show all / Hide all to control visibility.
* Search and select a net in the right Networks panel; ``Ctrl+F`` focuses its search.
  Searching preserves the active filter. Select All networks to reset it.
* Use Color and Opacity at the top to change colors and transparency.
* Use View to toggle the Layers panel, the grid, shape outlines, the flipped
  (bottom) view, component envelopes, reference names, and components on both
  sides. Components follow their actual placement layers; layer names need not
  be ``TOP`` or ``BOTTOM``.
* Use the info button to inspect scene details and unsupported geometry.

Picking and object properties
-----------------------------

Pick is enabled by default. Click a visible trace, via, pad or zone to inspect
it. Use the Pick button or ``P`` on the canvas to switch between picking and
pan-only navigation. A movement of more than four logical pixels starts a drag,
so clicking does not move the board. Middle/right drag always pans.

Hover uses an electric-blue outline (``#0057FF``). Selection uses vivid raspberry
(``#FF006E``), with a screen-space dot pattern for traces and zones. Both are
reserved colors outside the network CSS4 palette. A dark keyline separates the
highlights from similarly colored copper and the white background. The network
palette remains unchanged. Only visible layers and the active network filter participate
in picking. Filled zone holes are excluded. Click empty space, press ``Esc`` or
use the card's close button to clear selection.

The nonmodal card stays inside the canvas and follows the picked position while
panning and zooming. Narrow canvases use stacked, scrollable properties. Values
can be selected and copied. The card reports:

* Trace: name, signal (network) name, source width and centerline length. Length is for
  the picked EDB path, includes analytic circular arcs and excludes end-cap
  extensions; it is not a copper perimeter or a whole-network total.
* Via: name, network, copper diameter on the picked layer (or pad size for
  noncircular pads), drill diameter and the physical start/end layer span, even
  when only one layer is displayed. For slotted (rectangle, oval or bullet) drills
  the drill diameter is the larger slot dimension.
* Pad: network, owning component reference and component pin name/number.
* Zone: name and network.

Every card also reports the picked layer.

The properties and spatial index belong to the detached snapshot. Picking never
queries EDB and still works after the source session closes. Highlighting uses
the resident geometry; it does not rebuild or upload the board's geometry.

Within each layer, copper is composited in Zone, Trace, then Pad order. Fill
opacity defaults to 60%; reducing it reveals objects underneath. Every shape
receives a thin net-colored outline at full opacity, one screen pixel wide;
use ``plot_outlines=False`` or View > Outlines to hide it. Gray drill marks remain
visible on layers without copper pads.
Rectangle, oval and bullet (slotted) drills are cut out of the copper with their
true shape.
Component references use the same color as their outlines
and appear when there is enough room to read them.

Application integration
-----------------------

``edb.view_layout()`` runs the event loop when it creates ``QApplication``.
With an existing application, it returns after all source geometry has been
captured, without starting another application event loop. Call it on the GUI
thread and retain the returned window. The snapshot can then outlive its EDB
session. Standalone ``block=False`` callers must run or integrate the Qt event
loop themselves to continue preparing and displaying the snapshot.

Component display options use the same names as ``edb.nets.plot()``. Unlike
``edb.nets.plot()``, ``plot_components_on_both_side`` defaults to ``True``.
``plot_outlines`` controls shape outlines, and ``exact_component_bounds=True``
reads exact component envelopes instead of estimating them from pads:

.. code-block:: python

   window = edb.view_layout(
       plot_components=True,
       annotate_component_names=True,
       plot_components_on_both_side=True,
   )

Interacting from Python
-----------------------

The returned ``LayoutWindow`` reports user interaction through Qt signals and
accepts commands from Python. Call its methods on the GUI thread. The window
works on the detached snapshot, so selection and navigation commands never
query or modify EDB. ``refresh()`` explicitly reads the source session again.

.. code-block:: python

   window = edb.view_layout(block=False)


   def on_pick(picked):
       print(picked.kind, picked.object_id, picked.net, picked.layer)


   window.object_selected.connect(on_pick)
   window.net_changed.connect(print)

   window.select_net("GND")
   window.set_visible_layers(["TOP", "BOTTOM"])
   window.select_object(1234)
   window.zoom_to_net("GND")

Signals:

* ``object_selected(PickedObject)`` and ``selection_cleared()`` follow the
  picked object, whether from a click or ``select_object``.
* ``object_hovered(PickedObject | None)`` follows the hover highlight.
* ``net_changed(str | None)`` and ``visible_layers_changed(tuple[str, ...])``
  follow the Networks and Layers panels. Layer names are in stackup order.

A ``PickedObject`` is a detached value with ``object_id`` (the source EDB id),
``kind`` (``trace``, ``via``, ``pad`` or ``zone``), ``net``, ``layer`` and the full
``info`` (width, length, drill diameter, component, pin, and so on).

Properties and commands:

* ``selected_object``, ``selected_net`` and ``visible_layers`` return the current state.
* ``select_net(name)`` filters the view; ``None`` shows all networks.
* ``set_visible_layers(names)`` shows exactly those layers.
* ``select_object(object_id, kind=None, layer=None)`` selects as if picked.
  ``kind`` is needed only if an id exists for several kinds.
* ``clear_selection()``, ``fit_view()``, ``zoom_to_object(object_id, kind=None)``
  and ``zoom_to_net(name)`` control selection and camera.

Unknown nets, layers or object ids raise ``ValueError``. ``select_object`` and
``zoom_to_object`` raise ``RuntimeError`` while the layout is still loading.
Signals fire only on real changes, so applying the current state is a no-op.

Refresh and live modeling
-------------------------

Call ``window.refresh()`` after an edit to asynchronously recapture the current,
unsaved EDB layout in the same window. The capture uses the original layer,
network and geometry options. It preserves the camera, display settings,
visible layers that still exist, network search and active network filter.
Selection follows the source object id; deleting the selected object clears it.
The first geometry added to an empty scene is fitted automatically.

``refresh_finished(scene)`` reports that the replacement scene and picking data
are prepared; drawing follows in the Qt event loop. ``refresh_failed(error)``
reports a capture or preparation error and leaves the previous snapshot usable.
Overlapping refresh requests are merged into one subsequent refresh. Refresh
requires an open source session; windows opened from ``scene=`` are detached.

With ``edb.view_layout(live=True, block=False)``, supported PyEDB gRPC geometry
operations trigger refresh automatically. These include rectangle, circle,
polygon and trace creation, geometry property setters, moves, rotations,
scaling, void and Boolean operations, deletion, and padstack instance creation,
placement and property setters. Mutations through the raw ``.core`` API,
external processes, variable changes, component placement and stackup edits do
not emit these notifications; call ``refresh()`` explicitly after them. Keep
raw or otherwise untracked edits inside ``batch_update()`` when a live viewer
may be reading the same session, then request a refresh on the GUI thread.

Automatic updates are coalesced over ``refresh_interval`` milliseconds
(default 50). The initial load captures the full filtered layout. Subsequent
single-object copper edits and standalone via edits capture only the notified
objects. Unchanged contour values, triangulated meshes, GPU buffer ranges and
the main picking tree are retained. Added or replaced geometry is appended;
deleted ranges are excluded from drawing and picking without a geometry upload.
Network palette ids remain stable when new nets are added. Unchanged Layers
and Networks panels and component label textures are retained as well.

Boolean operations, void edits, component-owned pin edits and operations with
unknown dependencies conservatively recapture the full filtered layout.
``window.refresh()`` always requests a full recapture, including untracked
changes. The bounded change journal supports multiple independent windows;
a window that falls behind its retained history also recaptures fully.

To bound retained data during long editing sessions, geometry buffers and the
picking tree are compacted after 256 incremental updates or when estimated
invalidated data exceeds one third of resident geometry (with a 1 MiB floor).
Compaction rebuilds from the detached scene without rereading EDB. GPU buffer
growth and graphics device recreation require uploading the complete retained
buffer; ordinary updates with available capacity upload only the new tail.
The interval is a scheduling delay, not a frame-rate guarantee.
Source reads and supported geometry edits share a session lock, so a capture
cannot read a partially completed geometry operation. EDB close waits for an
active capture, stops live updates, and leaves the last snapshot available.
Closing the window unsubscribes updates and releases its source reference
after active capture and modeling tasks finish; it never closes EDB itself.

The Qt event loop must run while modeling. ``block=False`` alone does not run
that loop. For a standalone script, schedule a modeling callback with
``run_script()`` and run ``QApplication.exec()`` on the main thread:

.. code-block:: python

   import time

   from PySide6.QtWidgets import QApplication
   from pyedb import Edb

   app = QApplication.instance() or QApplication([])
   edb = Edb("board.aedb", grpc=True)  # Open a writable board with a TOP layer.
   window = edb.view_layout(live=True, block=False)
   window.set_visible_layers("TOP")


   def draw():
       for index in range(10):
           edb.modeler.create_rectangle(
               layer_name="TOP",
               net_name="GND",
               lower_left_point=[f"{index * 2}mm", "0mm"],
               upper_right_point=[f"{index * 2 + 1}mm", "1mm"],
           )
           time.sleep(0.2)  # Optional: make the construction steps visible.


   window.script_failed.connect(lambda error: print(f"Drawing failed: {error}"))
   window.run_script(draw)
   try:
       app.exec()
   finally:
       edb.close()

``run_script(callback, *args, **kwargs)`` runs one callback at a time on a worker
thread. The callback may access EDB, but must not access Qt widgets or call GUI
commands such as ``refresh()``. ``script_finished(result)`` and
``script_failed(error)`` report its outcome on the GUI thread. Script completion
and refresh completion are separate signals. In an existing Qt application,
use its running event loop instead of calling ``app.exec()`` again.

Use ``batch_update()`` inside the modeling callback to group many edits and
hold off capture until the group completes:

.. code-block:: python

   def draw_batch():
       with window.batch_update():
           for index in range(100):
               edb.modeler.create_circle(
                   layer_name="TOP",
                   x=f"{index}mm",
                   y="5mm",
                   radius="0.2mm",
                   net_name="GND",
               )


   window.run_script(draw_batch)

Batching controls notifications and read exclusion; it does not roll back edits
on failure. Successful edits before an exception still notify the viewer.
``window.stop_live()`` disables automatic updates while leaving manual refresh
available. Keep EDB open until modeling callbacks finish. For large layouts,
batch related changes to reduce captures and GPU submissions. Limit the initial
capture with ``layers`` / ``nets`` when only a subset is needed; hiding a layer
in the window affects drawing, not source capture. Incremental updates still
merge scene metadata and draw lists, so they do not make every CPU operation
independent of board size. Spatial streaming and multilevel geometry detail
are not currently implemented.

Graphics backends and platform requirements
------------------------------------------

The viewer targets 64-bit Windows 10/11 and mainstream glibc-based Linux
desktops from approximately the last four years. This includes Ubuntu LTS,
Debian, maintained Fedora releases, RHEL-compatible distributions and openSUSE.
Actual availability depends on the Python/Qt wheel, desktop libraries and GPU
driver, rather than the distribution's release date alone.

* Windows: Direct3D 11 is the default. Vulkan can be selected explicitly.
* Linux: Vulkan is selected explicitly on both X11 and Wayland. A working
  Vulkan loader and GPU driver are required; Mesa software Vulkan drivers can
  also be used for testing. There is no OpenGL fallback.
* macOS: the platform default is Metal. It is outside the Windows/Linux
  compatibility test matrix.

Use ``backend="vulkan"`` with ``edb.view_layout()`` or ``launch_viewer()``,
``--backend vulkan`` on the command line, or set ``PYEDB_VIEWER_BACKEND=vulkan``.
An explicit argument overrides the environment. ``auto`` selects the defaults
above. The status bar displays the selected renderer. Initialization failures
are reported in the canvas; the viewer does not silently change graphics APIs.
All RHI canvases inside one host top-level window must use the same graphics API.

PySide6 6.8.3 or later is required. The bundled shaders contain SPIR-V and HLSL
(and MSL for Metal), so running the viewer does not require a Vulkan SDK,
shader compiler, C++ compiler or PyOpenGL. Install the GPU vendor's Vulkan
driver; installing the Vulkan SDK alone does not install a GPU driver.

For current PySide6 wheels, the Linux x86-64 baseline is glibc 2.34; ARM64
wheels can require newer glibc and are not part of this compatibility target.
On older systems pip may select an older compatible PySide6 release. Use a
Python version supported by that release. Alpine/musl systems require a
separate Qt build and are outside the binary-wheel target.

For example, on Ubuntu/Debian X11 desktops, install the native dependencies
in addition to the Python extra:

.. code-block:: console

   sudo apt install libvulkan1 mesa-vulkan-drivers vulkan-tools libegl1 \
       libxkbcommon-x11-0 libxcb-cursor0 libxcb-icccm4 libxcb-keysyms1 \
       libxcb-render-util0 libxcb-xinerama0
   vulkaninfo --summary
   python -m pyedb.viewer --demo --backend vulkan

Use the distribution's Qt Wayland dependencies on a Wayland desktop. If Qt
chooses a different display plugin, ``QT_QPA_PLATFORM=xcb`` or
``QT_QPA_PLATFORM=wayland`` selects the session explicitly; this does not change
the Vulkan graphics backend. Remote/headless sessions need their own working
Vulkan presentation path. A display server alone does not provide a GPU driver.

The platform baselines above are deployment targets, not a claim that every
distribution, GPU and compositor combination has been tested. The automated
Linux matrix uses X11/Xvfb and Mesa Vulkan; Wayland and vendor GPU drivers need
desktop validation on the target machines.

Development and rendering tests
-------------------------------

Shader sources (``.vert``, ``.frag`` and ``.glsl``) are version-controlled;
generated ``.qsb`` packs are ignored by Git. The PEP 517 build backend compiles
fresh packs in a temporary staging tree when building a wheel, then delegates
the Python packaging to Flit. Building a wheel does not change the checkout.
An sdist contains the sources and build helpers, and compiles the packs when
it is converted into a wheel. Installing and running a built wheel never
invokes a shader compiler.

Build both distribution formats with a standard frontend:

.. code-block:: console

   python -m pip install build
   python -m build

Build isolation installs PySide6 as a build dependency to obtain its Qt Shader
Baker executable. It remains an optional ``viewer`` dependency at runtime.
Build services with an existing Qt toolchain may set ``PYEDB_QSB`` to the full
path of a compatible ``qsb`` executable instead. Metadata generation and
source-archive creation do not need Qt. Use a PEP 517 frontend such as
``python -m build``, ``pip wheel`` or ``uv build`` so the compilation hook runs.

Editable installs (``pip install -e ".[viewer]"``) generate ignored local packs
beside the source files. After editing shader sources in an editable checkout,
refresh those local packs with:

.. code-block:: console

   python tools/bake_viewer_shaders.py

Enable the desktop pixel and interaction regression tests:

.. code-block:: console

   PYEDB_VIEWER_RHI_TESTS=1 PYEDB_VIEWER_BACKEND=vulkan pytest \
       tests/integration/test_layout_viewer_rhi.py

Use PowerShell environment-variable syntax on Windows, and select ``d3d11``
to test the default Windows backend. Geometry preparation and picking unit
tests remain independent of a desktop and EDB license.

The licensed AEDB regression suite uses a writable temporary copy of
``tests/example_models/TEDB/ANSYS-HSD_V1.aedb``. It tests the checked-out source,
including local uncommitted changes, and verifies that the original fixture's
file hashes remain unchanged. It exercises native geometry creation, batched
notifications, incremental edits/deletion, standalone vias, void dependencies,
manual full capture and (when enabled) real GPU pixels and upload sizes. The
EDB session and geometry are real; capture spies only count calls.

An installed, licensed Ansys 2026 R1 or later is required by the gRPC backend.
Enable both the licensed and desktop tests on Windows with PowerShell:

.. code-block:: powershell

   $env:PYEDB_VIEWER_AEDB_TESTS = "1"
   $env:PYEDB_VIEWER_RHI_TESTS = "1"
   $env:PYEDB_VIEWER_EDB_VERSION = "2026.1"
   $env:PYEDB_VIEWER_BACKEND = "d3d11"
   python -m pytest tests/integration/test_layout_viewer_aedb.py -v --reruns 0

Without ``PYEDB_VIEWER_RHI_TESTS=1``, the licensed source/mesh tests can run
without a desktop. These tests are skipped unless
``PYEDB_VIEWER_AEDB_TESTS=1``; explicitly enabling them with an unsupported or
missing Ansys version produces a setup failure instead of a misleading pass.
``PYEDB_VIEWER_TEST_TIMEOUT`` controls the native viewer wait timeout in
seconds (default 180). Upload sizes and board counts are exposed through pytest
``record_property`` for JUnit reports.

Scope
-----

The viewer supports the gRPC EDB backend and reports extraction or rendering
failures in the interface.
3D component bodies, arbitrary source text, bondwires, polygonal drill profiles,
and backdrill profiles are not currently displayed. Thermal-relief pads
(round45/round90/square45/square90) are drawn as plain outlines without spokes.
Contour arcs use adaptive
subdivision with a default maximum chord error of 0.002 mm, based on radius and
sweep, with at most 10 degrees per segment. Thus a small semicircle uses at
least 18 segments and a full circle at least 36; larger radii receive more
segments when the sagitta bound requires them. Set ``chord_error`` /
``--chord-error`` to adjust this tolerance, or provide
``arc_segments`` / ``--arc-segments`` for a fixed count. Enable
``analytic_traces=True`` / ``--analytic-traces`` to retain analytic trace arcs.
