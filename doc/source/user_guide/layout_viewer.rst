Interactive 2D layout viewer
============================

The optional layout viewer displays copper, traces, pads, vias, and component
envelopes in a native PySide6 window using OpenGL. Its rendering design references
`Pomelo-Desktop <https://github.com/HaiwenZhang/Pomelo-Desktop>`_. Geometry remains
on the GPU during navigation and display changes.

Install and launch
------------------

.. code-block:: console

   pip install "pyedb[viewer]"
   python -m pyedb.viewer --demo
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

The viewer captures a detached snapshot without modifying or closing a
caller-owned EDB session. Reopen the viewer to display subsequent design changes.

All included layers are read on every open. The full viewer window appears
first and reports loading progress in its canvas. With ``progressive=True``
(the default), copper appears before pads and components finish loading;
the progress indicator disappears only after the complete layout is prepared,
uploaded and drawn. Changing layer visibility after loading requires no EDB
reads or geometry uploads. No scene or GPU data is saved to disk.

Display and navigation
----------------------

The workspace uses a light theme and a white canvas with an optional grid by
default. A dark theme with a dark canvas is also available: pass ``theme="dark"``
or ``--theme dark``, select View > Dark theme, or call ``window.set_theme("dark")``.
Switching themes keeps the view, selection and GPU geometry; copper, drill and
highlight colors are the same in both themes.
Color by Net is enabled by default, and only the first listed layer is initially
visible. Opacity defaults to 75%. Use ``color_by_net=False`` or
``--color-by-layer`` for layer colors.

.. code-block:: console

   python -m pyedb.viewer path/to/board.aedb --theme dark

* Drag with the left, middle, or right mouse button to pan; arrow keys also pan.
* Scroll to zoom around the pointer, or use ``+`` and ``-`` on the canvas.
* Use the floating navigation capsule to fit or zoom.
  ``F`` / ``Home`` fits the layout, and ``B`` flips the view when the canvas has focus.
* Use the left Layers panel checkboxes or Show all / Hide all to control visibility.
* Search and select a net in the right Networks panel; ``Ctrl+F`` focuses its search.
  Searching preserves the active filter. Select All networks to reset it.
* Use Color and Opacity at the top to change colors and transparency.
* Use View to toggle the Layers panel, the grid, shape outlines, the flipped
  (bottom) view, component envelopes, reference names, components on both
  sides, and the dark theme. Components follow their actual placement layers;
  layer names need not be ``TOP`` or ``BOTTOM``.
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

Within each layer, copper is composited in Zone, Trace, then Pad order. Reducing
opacity reveals objects underneath. By default every shape receives a thin
near-black outline, one screen pixel wide; use ``plot_outlines=False`` or View >
Outlines to hide it. Gray drill marks remain visible on layers without copper pads.
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
works on the detached snapshot, so these calls never query or modify EDB.

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
* ``theme_changed(str)`` reports ``"light"`` or ``"dark"`` when the theme changes.

A ``PickedObject`` is a detached value with ``object_id`` (the source EDB id),
``kind`` (``trace``, ``via``, ``pad`` or ``zone``), ``net``, ``layer`` and the full
``info`` (width, length, drill diameter, component, pin, and so on).

Properties and commands:

* ``selected_object``, ``selected_net``, ``visible_layers`` and ``theme`` return the current state.
* ``set_theme("light" | "dark")`` switches the workspace and canvas theme.
* ``select_net(name)`` filters the view; ``None`` shows all networks.
* ``set_visible_layers(names)`` shows exactly those layers.
* ``select_object(object_id, kind=None, layer=None)`` selects as if picked.
  ``kind`` is needed only if an id exists for several kinds.
* ``clear_selection()``, ``fit_view()``, ``zoom_to_object(object_id, kind=None)``
  and ``zoom_to_net(name)`` control selection and camera.

Unknown nets, layers or object ids raise ``ValueError``. ``select_object`` and
``zoom_to_object`` raise ``RuntimeError`` while the layout is still loading.
Signals fire only on real changes, so applying the current state is a no-op.

Requirements and scope
----------------------

An OpenGL 3.3 context with stencil support is required. The viewer supports the
gRPC backend and reports extraction or rendering failures in the interface.
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
