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

The demo generates its geometry in code and requires no sample files, EDB server,
or license. Opening an AEDB requires a supported
gRPC EDB installation and license. The command-line viewer opens the database
read-only and closes its session on exit.

To use an existing gRPC session:

.. code-block:: python

   from pyedb import Edb

   edb = Edb("board.aedb", grpc=True, isreadonly=True)
   try:
       window = edb.view_layout(block=True)
   finally:
       edb.close()

The viewer reads each requested layer without modifying or closing a caller-owned
EDB session. Keep that session open until the viewer closes. Each new window
reads its source again; no scene or GPU data is saved to disk.

Loading layers
--------------

Initially, only the first included conductor layer in stackup order is loaded
(usually TOP), including its copper, pads, vias and components. The same window
shows progress throughout loading. Other layers remain marked On demand until
their checkboxes are enabled. Show all requests every included layer.

Layers load sequentially in a background worker while the existing view remains
interactive. Loading another layer preserves the camera, network selection and
resident geometry. Loaded layers remain in memory for this window, so hiding and
showing them requires no new reads. Toggle a failed layer off and on to retry.
Closing during a read hides the window and drains the active read before
releasing the source.

Current EDB servers still enumerate the complete primitive and padstack
collections to build a layer index. Hidden layers skip detailed geometry
extraction, arc subdivision, triangulation and GPU uploads; enumeration itself
is not a server-side layer-filtered read.

For a detached full capture, use ``edb.view_layout(on_demand=False)`` or
``python -m pyedb.viewer path/to/board.aedb --eager``. A detached window can outlive
its source session after capture completes.

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
* Use View to toggle the grid, component envelopes, reference names, and
  components on both sides. Components follow their actual placement layers;
  layer names need not be ``TOP`` or ``BOTTOM``.
* Use the info button to inspect scene details and unsupported geometry.

Within each layer, copper is composited in Zone, Trace, then Pad order. Reducing
opacity reveals objects underneath. Pins retain their copper fill without
additional borders. Gray drill marks remain visible on layers without copper pads.
Component references use the same color as their outlines
and appear when there is enough room to read them.

Application integration
-----------------------

``edb.view_layout()`` runs the event loop when it creates ``QApplication``.
With an existing application, it returns after the initial layer has been
captured, without starting another application event loop. Call it on the GUI
thread and retain the returned window. With on-demand loading, keep the EDB
session open until ``window.closed`` is emitted. Standalone ``block=False``
callers must run or integrate the Qt event loop themselves.

Component display options use the same names as ``edb.nets.plot()``:

.. code-block:: python

   window = edb.view_layout(
       plot_components=True,
       annotate_component_names=True,
       plot_components_on_both_side=True,
   )

Requirements and scope
----------------------

An OpenGL 3.3 context with stencil support is required. The viewer supports the
gRPC backend and reports extraction or rendering failures in the interface.
3D component bodies, arbitrary source text, bondwires, slotted drills, and
backdrill profiles are not currently displayed. Contour arcs use adaptive
subdivision with a default maximum chord error of 0.01 mm, based on radius and
sweep. Set ``chord_error`` / ``--chord-error`` to adjust this tolerance, or provide
``arc_segments`` / ``--arc-segments`` for a fixed count. Enable
``analytic_traces=True`` / ``--analytic-traces`` to retain analytic trace arcs.
