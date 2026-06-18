.. _ref_release_notes:

Release notes
#############

This document contains the release notes for the project.

.. vale off

.. towncrier release notes start

`0.78.0 <https://github.com/ansys/pyedb/releases/tag/v0.78.0>`_ - June 18, 2026
===============================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Vendor libraries adding support with cfg
          - `#2243 <https://github.com/ansys/pyedb/pull/2243>`_

        * - Issue #2248 implemented
          - `#2249 <https://github.com/ansys/pyedb/pull/2249>`_

        * - Insert coordinate system
          - `#2255 <https://github.com/ansys/pyedb/pull/2255>`_

        * - Packagedef bound
          - `#2289 <https://github.com/ansys/pyedb/pull/2289>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Issue #2075 fixed
          - `#2242 <https://github.com/ansys/pyedb/pull/2242>`_

        * - Vertical edge port reference layer failing
          - `#2244 <https://github.com/ansys/pyedb/pull/2244>`_

        * - Component.py pins
          - `#2245 <https://github.com/ansys/pyedb/pull/2245>`_

        * - Place 3D Component on a component
          - `#2250 <https://github.com/ansys/pyedb/pull/2250>`_

        * - Issue #2262 fixed
          - `#2263 <https://github.com/ansys/pyedb/pull/2263>`_

        * - Issue #2264 fixed
          - `#2265 <https://github.com/ansys/pyedb/pull/2265>`_

        * - Issue #2258 fixed
          - `#2266 <https://github.com/ansys/pyedb/pull/2266>`_

        * - Issue #2285 fix
          - `#2286 <https://github.com/ansys/pyedb/pull/2286>`_

        * - Issue 2284 fix extended net fix
          - `#2288 <https://github.com/ansys/pyedb/pull/2288>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Bump actions/checkout from 6.0.2 to 6.0.3
          - `#2267 <https://github.com/ansys/pyedb/pull/2267>`_

        * - Bump black from 25.1.0 to 26.5.1
          - `#2269 <https://github.com/ansys/pyedb/pull/2269>`_

        * - Bump astral-sh/setup-uv from 8.1.0 to 8.2.0
          - `#2270 <https://github.com/ansys/pyedb/pull/2270>`_

        * - Bump ruff from 0.15.13 to 0.15.16
          - `#2271 <https://github.com/ansys/pyedb/pull/2271>`_

        * - Bump pytest-rerunfailures from 16.2 to 16.3
          - `#2272 <https://github.com/ansys/pyedb/pull/2272>`_

        * - Bump pytest-xdist from 3.6.1 to 3.8.0
          - `#2273 <https://github.com/ansys/pyedb/pull/2273>`_

        * - Bump jupyterlab from 4.5.7 to 4.5.8
          - `#2274 <https://github.com/ansys/pyedb/pull/2274>`_

        * - Bump pywin32 from 311 to 312
          - `#2275 <https://github.com/ansys/pyedb/pull/2275>`_

        * - Bump codecov/codecov-action from 6.0.1 to 7.0.0
          - `#2282 <https://github.com/ansys/pyedb/pull/2282>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Pre-commit automatic update
          - `#2226 <https://github.com/ansys/pyedb/pull/2226>`_, `#2277 <https://github.com/ansys/pyedb/pull/2277>`_

        * - Bump release 0.78.dev0
          - `#2235 <https://github.com/ansys/pyedb/pull/2235>`_

        * - Update CHANGELOG for v0.77.0
          - `#2241 <https://github.com/ansys/pyedb/pull/2241>`_

        * - CI adjusted
          - `#2257 <https://github.com/ansys/pyedb/pull/2257>`_

        * - Removing grpc support with 25.2
          - `#2261 <https://github.com/ansys/pyedb/pull/2261>`_

        * - Remove reviewers and add pre-commit in dependabot cfg
          - `#2268 <https://github.com/ansys/pyedb/pull/2268>`_

        * - CI release windows fix
          - `#2279 <https://github.com/ansys/pyedb/pull/2279>`_

        * - Removing failing tests on pyaedt linux
          - `#2283 <https://github.com/ansys/pyedb/pull/2283>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Remove redundant methods in gRPC
          - `#2254 <https://github.com/ansys/pyedb/pull/2254>`_


`0.77.0 <https://github.com/ansys/pyedb/releases/tag/v0.77.0>`_ - June 05, 2026
===============================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Sp2 preparation
          - `#2221 <https://github.com/ansys/pyedb/pull/2221>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Pathlib.path support
          - `#2189 <https://github.com/ansys/pyedb/pull/2189>`_

        * - Issue #2003 fix
          - `#2190 <https://github.com/ansys/pyedb/pull/2190>`_

        * - Auto parametrize grpc fix
          - `#2197 <https://github.com/ansys/pyedb/pull/2197>`_

        * - HFSS-PI simulation setup cast failing
          - `#2199 <https://github.com/ansys/pyedb/pull/2199>`_

        * - EDB CFG terminal improvement padstack instance id
          - `#2205 <https://github.com/ansys/pyedb/pull/2205>`_

        * - Issue 2210 fix
          - `#2212 <https://github.com/ansys/pyedb/pull/2212>`_

        * - Issue #2214 fixed
          - `#2215 <https://github.com/ansys/pyedb/pull/2215>`_

        * - Edb cfg efficiency and terminal support
          - `#2216 <https://github.com/ansys/pyedb/pull/2216>`_

        * - Issue #2213 fixed
          - `#2217 <https://github.com/ansys/pyedb/pull/2217>`_

        * - Issue #2211 fixed
          - `#2218 <https://github.com/ansys/pyedb/pull/2218>`_

        * - Add missing parameter to the action
          - `#2223 <https://github.com/ansys/pyedb/pull/2223>`_

        * - Issue #2224 fix
          - `#2225 <https://github.com/ansys/pyedb/pull/2225>`_

        * - Issue #2020 fix
          - `#2228 <https://github.com/ansys/pyedb/pull/2228>`_

        * - CI activation for Windows virtual environment
          - `#2238 <https://github.com/ansys/pyedb/pull/2238>`_

        * - Bugs fix
          - `#2240 <https://github.com/ansys/pyedb/pull/2240>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Bump ansys/actions from 10.3.0 to 10.3.1
          - `#2203 <https://github.com/ansys/pyedb/pull/2203>`_

        * - Bump codecov/codecov-action from 6.0.0 to 6.0.1
          - `#2219 <https://github.com/ansys/pyedb/pull/2219>`_

        * - Bump ansys/actions from 10.3.1 to 10.3.2
          - `#2229 <https://github.com/ansys/pyedb/pull/2229>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Uv support added
          - `#2182 <https://github.com/ansys/pyedb/pull/2182>`_

        * - Update CHANGELOG for v0.76.0
          - `#2187 <https://github.com/ansys/pyedb/pull/2187>`_

        * - Bump release 0.77.dev0
          - `#2188 <https://github.com/ansys/pyedb/pull/2188>`_

        * - Layout primitive test coverage
          - `#2191 <https://github.com/ansys/pyedb/pull/2191>`_

        * - Modeler test coverage
          - `#2192 <https://github.com/ansys/pyedb/pull/2192>`_

        * - Components coverage increase
          - `#2193 <https://github.com/ansys/pyedb/pull/2193>`_

        * - Padstack coverage
          - `#2194 <https://github.com/ansys/pyedb/pull/2194>`_

        * - Nets test coverage
          - `#2195 <https://github.com/ansys/pyedb/pull/2195>`_

        * - System test reorganized
          - `#2196 <https://github.com/ansys/pyedb/pull/2196>`_

        * - Source-excitation coverage increase
          - `#2201 <https://github.com/ansys/pyedb/pull/2201>`_

        * - Stackup coverage increase
          - `#2202 <https://github.com/ansys/pyedb/pull/2202>`_

        * - Pre-commit automatic update
          - `#2204 <https://github.com/ansys/pyedb/pull/2204>`_

        * - More unit test added
          - `#2222 <https://github.com/ansys/pyedb/pull/2222>`_

        * - Cleanup workflows and leverage python 3.14
          - `#2231 <https://github.com/ansys/pyedb/pull/2231>`_

        * - Adding grpc message
          - `#2232 <https://github.com/ansys/pyedb/pull/2232>`_

        * - Release issues with uv
          - `#2236 <https://github.com/ansys/pyedb/pull/2236>`_


`0.76.0 <https://github.com/ansys/pyedb/releases/tag/v0.76.0>`_ - May 22, 2026
==============================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Configuration API and documentation
          - `#2181 <https://github.com/ansys/pyedb/pull/2181>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Rpc session start issue #2105
          - `#2119 <https://github.com/ansys/pyedb/pull/2119>`_

        * - Layer type
          - `#2121 <https://github.com/ansys/pyedb/pull/2121>`_

        * - Bug in cfg padstack backdrill
          - `#2130 <https://github.com/ansys/pyedb/pull/2130>`_

        * - Bug cfg backdrill
          - `#2131 <https://github.com/ansys/pyedb/pull/2131>`_

        * - Siwave DC setup fix
          - `#2143 <https://github.com/ansys/pyedb/pull/2143>`_

        * - Run ruff select D
          - `#2154 <https://github.com/ansys/pyedb/pull/2154>`_

        * - Issue #2151 fix
          - `#2156 <https://github.com/ansys/pyedb/pull/2156>`_

        * - Ruff rules
          - `#2173 <https://github.com/ansys/pyedb/pull/2173>`_

        * - Unpin dependencies
          - `#2180 <https://github.com/ansys/pyedb/pull/2180>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update \`\`CONTRIBUTORS.md\`\` with the latest contributors
          - `#2122 <https://github.com/ansys/pyedb/pull/2122>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Bump ansys/actions from 10.2.12 to 10.3.0
          - `#2132 <https://github.com/ansys/pyedb/pull/2132>`_

        * - Bump actions/labeler from 6.0.1 to 6.1.0
          - `#2153 <https://github.com/ansys/pyedb/pull/2153>`_

        * - Update ansys-sphinx-theme requirement from <1.8,>=1.0.0 to >=1.0.0,<1.9
          - `#2178 <https://github.com/ansys/pyedb/pull/2178>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update CHANGELOG for v0.75.0
          - `#2116 <https://github.com/ansys/pyedb/pull/2116>`_

        * - Bump dev version and cleanup
          - `#2117 <https://github.com/ansys/pyedb/pull/2117>`_

        * - Fixing random test failing
          - `#2120 <https://github.com/ansys/pyedb/pull/2120>`_

        * - Typo fix
          - `#2127 <https://github.com/ansys/pyedb/pull/2127>`_

        * - Pre-commit automatic update
          - `#2174 <https://github.com/ansys/pyedb/pull/2174>`_

        * - Configuration coverage improved
          - `#2183 <https://github.com/ansys/pyedb/pull/2183>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Configuration stackup
          - `#2124 <https://github.com/ansys/pyedb/pull/2124>`_

        * - Cfg boundaries
          - `#2133 <https://github.com/ansys/pyedb/pull/2133>`_

        * - Cfg common
          - `#2134 <https://github.com/ansys/pyedb/pull/2134>`_

        * - Cfg general refactoring
          - `#2136 <https://github.com/ansys/pyedb/pull/2136>`_

        * - Cfg modeler refactoring
          - `#2137 <https://github.com/ansys/pyedb/pull/2137>`_

        * - Cfg nets refactoring
          - `#2138 <https://github.com/ansys/pyedb/pull/2138>`_

        * - Cfg_operations refactoring
          - `#2139 <https://github.com/ansys/pyedb/pull/2139>`_

        * - Cfg_package_definition refactoring
          - `#2140 <https://github.com/ansys/pyedb/pull/2140>`_

        * - Cfg_padstack
          - `#2141 <https://github.com/ansys/pyedb/pull/2141>`_

        * - Cfg pingroup refactoring
          - `#2144 <https://github.com/ansys/pyedb/pull/2144>`_

        * - Cfg ports refactoring
          - `#2145 <https://github.com/ansys/pyedb/pull/2145>`_

        * - Cfg s parameters refactoring
          - `#2146 <https://github.com/ansys/pyedb/pull/2146>`_

        * - Cfg setups refactoring
          - `#2147 <https://github.com/ansys/pyedb/pull/2147>`_

        * - Cfg spice refactoring
          - `#2148 <https://github.com/ansys/pyedb/pull/2148>`_

        * - Cfg stackup refactoring
          - `#2149 <https://github.com/ansys/pyedb/pull/2149>`_

        * - Cfg terminal refactoring
          - `#2150 <https://github.com/ansys/pyedb/pull/2150>`_

        * - Cfg components refactoring
          - `#2157 <https://github.com/ansys/pyedb/pull/2157>`_


`0.75.0 <https://github.com/ansys/pyedb/releases/tag/v0.75.0>`_ - May 05, 2026
==============================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Components solder ball property added
          - `#2103 <https://github.com/ansys/pyedb/pull/2103>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update sphinx-gallery requirement from <0.21,>=0.14.0 to >=0.14.0,<0.22
          - `#2106 <https://github.com/ansys/pyedb/pull/2106>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Regex fix
          - `#2098 <https://github.com/ansys/pyedb/pull/2098>`_

        * - Rpc session fix
          - `#2107 <https://github.com/ansys/pyedb/pull/2107>`_

        * - Enabling skipped tests
          - `#2109 <https://github.com/ansys/pyedb/pull/2109>`_

        * - Net.py missing class import
          - `#2111 <https://github.com/ansys/pyedb/pull/2111>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Add dotnet install target
          - `#2078 <https://github.com/ansys/pyedb/pull/2078>`_

        * - Update CHANGELOG for v0.74.0
          - `#2091 <https://github.com/ansys/pyedb/pull/2091>`_

        * - Pre-commit automatic update
          - `#2092 <https://github.com/ansys/pyedb/pull/2092>`_, `#2115 <https://github.com/ansys/pyedb/pull/2115>`_

        * - Bump dev version into v0.75.dev0
          - `#2094 <https://github.com/ansys/pyedb/pull/2094>`_

        * - AGENT file added for helping contributors
          - `#2104 <https://github.com/ansys/pyedb/pull/2104>`_

        * - Grpc internal deprecated call removal
          - `#2110 <https://github.com/ansys/pyedb/pull/2110>`_


`0.74.0 <https://github.com/ansys/pyedb/releases/tag/v0.74.0>`_ - April 27, 2026
================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Issue 2073 cutout export only extent
          - `#2088 <https://github.com/ansys/pyedb/pull/2088>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Documentation improvement
          - `#2085 <https://github.com/ansys/pyedb/pull/2085>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Coverage rects
          - `#2083 <https://github.com/ansys/pyedb/pull/2083>`_

        * - Example fix
          - `#2090 <https://github.com/ansys/pyedb/pull/2090>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update CHANGELOG for v0.73.0
          - `#2082 <https://github.com/ansys/pyedb/pull/2082>`_

        * - Bump dev 0.74.dev0 version
          - `#2086 <https://github.com/ansys/pyedb/pull/2086>`_

        * - Update code owners to help with maintenance
          - `#2089 <https://github.com/ansys/pyedb/pull/2089>`_


`0.73.0 <https://github.com/ansys/pyedb/releases/tag/v0.73.0>`_ - April 24, 2026
================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Solder mask auto opening
          - `#2060 <https://github.com/ansys/pyedb/pull/2060>`_

        * - Etch net class feature added
          - `#2069 <https://github.com/ansys/pyedb/pull/2069>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Bump actions/upload-artifact from 7.0.0 to 7.0.1
          - `#2061 <https://github.com/ansys/pyedb/pull/2061>`_

        * - Update pydantic requirement from <2.13,>=2.6.4 to >=2.6.4,<2.14
          - `#2062 <https://github.com/ansys/pyedb/pull/2062>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Documentation improvement
          - `#2058 <https://github.com/ansys/pyedb/pull/2058>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Pyedb grpc extensions fix
          - `#2064 <https://github.com/ansys/pyedb/pull/2064>`_

        * - Multiple edb load fix
          - `#2066 <https://github.com/ansys/pyedb/pull/2066>`_

        * - Refactor dotnet imports to avoid crash at Edb init
          - `#2070 <https://github.com/ansys/pyedb/pull/2070>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update CHANGELOG for v0.72.0
          - `#2050 <https://github.com/ansys/pyedb/pull/2050>`_

        * - Test dotnet fix
          - `#2051 <https://github.com/ansys/pyedb/pull/2051>`_

        * - Update license metadata in pyproject.toml
          - `#2052 <https://github.com/ansys/pyedb/pull/2052>`_

        * - Pre-commit automatic update
          - `#2063 <https://github.com/ansys/pyedb/pull/2063>`_

        * - Bump ansys-edb-core into v0.3.1
          - `#2074 <https://github.com/ansys/pyedb/pull/2074>`_

        * - Pyaedt alignment
          - `#2076 <https://github.com/ansys/pyedb/pull/2076>`_

        * - Update pyaedt testing on release
          - `#2079 <https://github.com/ansys/pyedb/pull/2079>`_

        * - Extend timeout for release
          - `#2081 <https://github.com/ansys/pyedb/pull/2081>`_


`0.72.0 <https://github.com/ansys/pyedb/releases/tag/v0.72.0>`_ - April 17, 2026
================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Xml roughness etch
          - `#1940 <https://github.com/ansys/pyedb/pull/1940>`_

        * - Grpc in memory new feature for SP1
          - `#1974 <https://github.com/ansys/pyedb/pull/1974>`_

        * - Path coverage
          - `#1998 <https://github.com/ansys/pyedb/pull/1998>`_

        * - RF trace taper
          - `#2008 <https://github.com/ansys/pyedb/pull/2008>`_

        * - Horizontal wave port
          - `#2031 <https://github.com/ansys/pyedb/pull/2031>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Bump pyvista/setup-headless-display-action from 4.2 to 4.3
          - `#1938 <https://github.com/ansys/pyedb/pull/1938>`_

        * - Bump actions/download-artifact from 8.0.0 to 8.0.1
          - `#1950 <https://github.com/ansys/pyedb/pull/1950>`_

        * - Update pypandoc requirement from <1.17,>=1.10.0 to >=1.10.0,<1.18
          - `#1951 <https://github.com/ansys/pyedb/pull/1951>`_

        * - Bump nick-fields/retry from 3.0.2 to 4.0.0
          - `#1975 <https://github.com/ansys/pyedb/pull/1975>`_

        * - Update pytest-cov requirement from <7.1,>=4.0.0 to >=4.0.0,<7.2
          - `#1976 <https://github.com/ansys/pyedb/pull/1976>`_

        * - Bump codecov/codecov-action from 5.5.2 to 6.0.0
          - `#1994 <https://github.com/ansys/pyedb/pull/1994>`_

        * - Bump pypa/gh-action-pypi-publish from 1.13.0 to 1.14.0
          - `#2013 <https://github.com/ansys/pyedb/pull/2013>`_

        * - Bump ansys/actions from 10.2.7 to 10.2.12
          - `#2027 <https://github.com/ansys/pyedb/pull/2027>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Add_sweep method doc string
          - `#1956 <https://github.com/ansys/pyedb/pull/1956>`_

        * - Doc string
          - `#1964 <https://github.com/ansys/pyedb/pull/1964>`_

        * - Add LLM-friendly files, backend compatibility page, and new-user README path
          - `#1970 <https://github.com/ansys/pyedb/pull/1970>`_

        * - Documentation improvement
          - `#1996 <https://github.com/ansys/pyedb/pull/1996>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Issue #1930 fix
          - `#1941 <https://github.com/ansys/pyedb/pull/1941>`_

        * - Issue #1936 grpc cutout multithread with preserve model pin
          - `#1942 <https://github.com/ansys/pyedb/pull/1942>`_

        * - Issue 1939 fix grpc Terminal not set as reference causing random failure on SIwave
          - `#1944 <https://github.com/ansys/pyedb/pull/1944>`_

        * - Wave port terminal fixed issue #1909
          - `#1945 <https://github.com/ansys/pyedb/pull/1945>`_

        * - Issue#1407 solder ball shape none
          - `#1946 <https://github.com/ansys/pyedb/pull/1946>`_

        * - Issue #1063 fixed source to ground
          - `#1947 <https://github.com/ansys/pyedb/pull/1947>`_

        * - Issue#1900 padstacks def
          - `#1948 <https://github.com/ansys/pyedb/pull/1948>`_

        * - Add all PyAEDT Extension tests
          - `#1949 <https://github.com/ansys/pyedb/pull/1949>`_

        * - No stable version
          - `#1960 <https://github.com/ansys/pyedb/pull/1960>`_

        * - Enabling pyaedt warning propagation
          - `#1961 <https://github.com/ansys/pyedb/pull/1961>`_

        * - Grpc materials fixed
          - `#1966 <https://github.com/ansys/pyedb/pull/1966>`_

        * - Remove dotnetcore2
          - `#1972 <https://github.com/ansys/pyedb/pull/1972>`_

        * - Expose Edb deprecations statically for grpc and dotnet backends
          - `#1980 <https://github.com/ansys/pyedb/pull/1980>`_

        * - Issue#1979 set solder ball material
          - `#1982 <https://github.com/ansys/pyedb/pull/1982>`_

        * - Issue#1969 fix bondwire missing primitive attribute
          - `#1984 <https://github.com/ansys/pyedb/pull/1984>`_

        * - Stackup.py roughness import
          - `#1985 <https://github.com/ansys/pyedb/pull/1985>`_

        * - Grpc import xml with roughness
          - `#1986 <https://github.com/ansys/pyedb/pull/1986>`_

        * - Auto_mesh_operation
          - `#1989 <https://github.com/ansys/pyedb/pull/1989>`_

        * - Text in prims
          - `#1992 <https://github.com/ansys/pyedb/pull/1992>`_

        * - Physical merged fixed
          - `#1999 <https://github.com/ansys/pyedb/pull/1999>`_

        * - Coverage rects and bugs in functions
          - `#2007 <https://github.com/ansys/pyedb/pull/2007>`_

        * - Grpc value.py
          - `#2012 <https://github.com/ansys/pyedb/pull/2012>`_

        * - Remove pyaedt code
          - `#2019 <https://github.com/ansys/pyedb/pull/2019>`_

        * - Insert layout instance
          - `#2020 <https://github.com/ansys/pyedb/pull/2020>`_

        * - Grpc information
          - `#2022 <https://github.com/ansys/pyedb/pull/2022>`_

        * - Improve grpc Nets.delete performance for large net deletions
          - `#2034 <https://github.com/ansys/pyedb/pull/2034>`_

        * - DotNet GC fix with release 2026.1
          - `#2037 <https://github.com/ansys/pyedb/pull/2037>`_

        * - Bug dotnet import with gpc fix
          - `#2039 <https://github.com/ansys/pyedb/pull/2039>`_

        * - Guard gRPC layout terminal enumeration against null terminals
          - `#2040 <https://github.com/ansys/pyedb/pull/2040>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update CHANGELOG for v0.71.0
          - `#1934 <https://github.com/ansys/pyedb/pull/1934>`_

        * - Bump release 0.72.dev0
          - `#1935 <https://github.com/ansys/pyedb/pull/1935>`_

        * - Pre-commit automatic update
          - `#1952 <https://github.com/ansys/pyedb/pull/1952>`_, `#1977 <https://github.com/ansys/pyedb/pull/1977>`_, `#2002 <https://github.com/ansys/pyedb/pull/2002>`_, `#2033 <https://github.com/ansys/pyedb/pull/2033>`_

        * - Migrate \`\`pyedb\`\` CI to AEDT 2026.1
          - `#2014 <https://github.com/ansys/pyedb/pull/2014>`_

        * - Fix pyaedt testing missing dependencies
          - `#2042 <https://github.com/ansys/pyedb/pull/2042>`_

        * - Timeout
          - `#2047 <https://github.com/ansys/pyedb/pull/2047>`_

        * - Ansys edb core version for release
          - `#2049 <https://github.com/ansys/pyedb/pull/2049>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Grpc primitive queries refactoring
          - `#1916 <https://github.com/ansys/pyedb/pull/1916>`_


`0.71.0 <https://github.com/ansys/pyedb/releases/tag/v0.71.0>`_ - March 20, 2026
================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Physical merge
          - `#1830 <https://github.com/ansys/pyedb/pull/1830>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Bump actions/setup-python from 6.1.0 to 6.2.0
          - `#1772 <https://github.com/ansys/pyedb/pull/1772>`_, `#1890 <https://github.com/ansys/pyedb/pull/1890>`_

        * - Update jupytext requirement from <1.19,>=1.16.0 to >=1.16.0,<1.20
          - `#1779 <https://github.com/ansys/pyedb/pull/1779>`_

        * - Bump actions/upload-artifact from 6.0.0 to 7.0.0
          - `#1863 <https://github.com/ansys/pyedb/pull/1863>`_, `#1876 <https://github.com/ansys/pyedb/pull/1876>`_

        * - Bump actions/download-artifact from 7.0.0 to 8.0.0
          - `#1864 <https://github.com/ansys/pyedb/pull/1864>`_

        * - Bump ansys/actions from 10.2.4 to 10.2.7
          - `#1865 <https://github.com/ansys/pyedb/pull/1865>`_, `#1877 <https://github.com/ansys/pyedb/pull/1877>`_

        * - Update ansys-sphinx-theme[autoapi] requirement from <1.7,>=1.0.0 to >=1.0.0,<1.8
          - `#1915 <https://github.com/ansys/pyedb/pull/1915>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Adding DJ model docstring with add method
          - `#1847 <https://github.com/ansys/pyedb/pull/1847>`_

        * - Clean dotnet database geometry
          - `#1855 <https://github.com/ansys/pyedb/pull/1855>`_

        * - Reverting .NET documentation
          - `#1861 <https://github.com/ansys/pyedb/pull/1861>`_

        * - Design navigation - getting started with pyedb documentation
          - `#1919 <https://github.com/ansys/pyedb/pull/1919>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Unittest
          - `#1826 <https://github.com/ansys/pyedb/pull/1826>`_

        * - Syntax issues
          - `#1837 <https://github.com/ansys/pyedb/pull/1837>`_

        * - Configuration.py
          - `#1845 <https://github.com/ansys/pyedb/pull/1845>`_

        * - Insert layout component
          - `#1869 <https://github.com/ansys/pyedb/pull/1869>`_

        * - Fixed 2 tests in grpc
          - `#1870 <https://github.com/ansys/pyedb/pull/1870>`_

        * - Cfg tests 2026.1 fix
          - `#1873 <https://github.com/ansys/pyedb/pull/1873>`_

        * - Hfss simulation setup grpc
          - `#1874 <https://github.com/ansys/pyedb/pull/1874>`_

        * - Improve docstring and coverage for .net
          - `#1878 <https://github.com/ansys/pyedb/pull/1878>`_

        * - Test robustness
          - `#1882 <https://github.com/ansys/pyedb/pull/1882>`_

        * - Grpc cfg layer stackup test fix
          - `#1884 <https://github.com/ansys/pyedb/pull/1884>`_

        * - Downloads features
          - `#1885 <https://github.com/ansys/pyedb/pull/1885>`_

        * - Rf lib fixed
          - `#1886 <https://github.com/ansys/pyedb/pull/1886>`_

        * - RaptorX + HFSS-PI fixed and refactoring after edb-core changes
          - `#1888 <https://github.com/ansys/pyedb/pull/1888>`_

        * - Test_drc_rules_from_file_grpc_fixed
          - `#1889 <https://github.com/ansys/pyedb/pull/1889>`_

        * - Place 3dcomp and 3dlcomp
          - `#1896 <https://github.com/ansys/pyedb/pull/1896>`_

        * - Micro via fixed
          - `#1901 <https://github.com/ansys/pyedb/pull/1901>`_

        * - Removing grpc warnings
          - `#1904 <https://github.com/ansys/pyedb/pull/1904>`_

        * - Grpc end cap style setter for traces
          - `#1907 <https://github.com/ansys/pyedb/pull/1907>`_

        * - Issue #1853 fix compute arc
          - `#1908 <https://github.com/ansys/pyedb/pull/1908>`_

        * - Update python requirement to 3.10
          - `#1913 <https://github.com/ansys/pyedb/pull/1913>`_

        * - Pydantic warnings
          - `#1914 <https://github.com/ansys/pyedb/pull/1914>`_

        * - Components getitem
          - `#1922 <https://github.com/ansys/pyedb/pull/1922>`_

        * - LINUX_WARNING: Update link
          - `#1924 <https://github.com/ansys/pyedb/pull/1924>`_

        * - Issue #1926 fix cfg export
          - `#1928 <https://github.com/ansys/pyedb/pull/1928>`_

        * - Issue #1618
          - `#1929 <https://github.com/ansys/pyedb/pull/1929>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update CHANGELOG for v0.69.0
          - `#1825 <https://github.com/ansys/pyedb/pull/1825>`_

        * - Bump release 0.70.dev0
          - `#1827 <https://github.com/ansys/pyedb/pull/1827>`_

        * - Clean up root level files
          - `#1836 <https://github.com/ansys/pyedb/pull/1836>`_

        * - Group test dependencies
          - `#1840 <https://github.com/ansys/pyedb/pull/1840>`_

        * - Pre-commit automatic update
          - `#1844 <https://github.com/ansys/pyedb/pull/1844>`_, `#1879 <https://github.com/ansys/pyedb/pull/1879>`_, `#1894 <https://github.com/ansys/pyedb/pull/1894>`_, `#1917 <https://github.com/ansys/pyedb/pull/1917>`_

        * - Split into multiple workflows and clean up
          - `#1856 <https://github.com/ansys/pyedb/pull/1856>`_

        * - Add dependabot cooldown settings
          - `#1868 <https://github.com/ansys/pyedb/pull/1868>`_

        * - Rework main workflow to only build doc and upload dev docs
          - `#1887 <https://github.com/ansys/pyedb/pull/1887>`_

        * - Removing IDE warnings and fixing minor issues
          - `#1891 <https://github.com/ansys/pyedb/pull/1891>`_

        * - Update code owners
          - `#1892 <https://github.com/ansys/pyedb/pull/1892>`_

        * - Add codacy configuration file and badge
          - `#1893 <https://github.com/ansys/pyedb/pull/1893>`_

        * - Deprecation decorator
          - `#1895 <https://github.com/ansys/pyedb/pull/1895>`_

        * - Update CHANGELOG for v0.70.0
          - `#1899 <https://github.com/ansys/pyedb/pull/1899>`_

        * - Bump dev version into v0.71.dev0
          - `#1905 <https://github.com/ansys/pyedb/pull/1905>`_

        * - Removing dotnet warnings
          - `#1906 <https://github.com/ansys/pyedb/pull/1906>`_

        * - Release 2026.1 stable
          - `#1918 <https://github.com/ansys/pyedb/pull/1918>`_

        * - Moving optional dependencies to default
          - `#1927 <https://github.com/ansys/pyedb/pull/1927>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Lazy import and dependency rework
          - `#1828 <https://github.com/ansys/pyedb/pull/1828>`_

        * - Constants alignment between grpc dotnet
          - `#1829 <https://github.com/ansys/pyedb/pull/1829>`_

        * - Em properties
          - `#1842 <https://github.com/ansys/pyedb/pull/1842>`_

        * - Grpc warning messages added -> default DotNet
          - `#1846 <https://github.com/ansys/pyedb/pull/1846>`_

        * - Refactor grpc for configuration enablement
          - `#1857 <https://github.com/ansys/pyedb/pull/1857>`_

        * - XML control file unification
          - `#1866 <https://github.com/ansys/pyedb/pull/1866>`_

        * - Get_primitives
          - `#1867 <https://github.com/ansys/pyedb/pull/1867>`_

        * - Clean modeler
          - `#1872 <https://github.com/ansys/pyedb/pull/1872>`_

        * - Add deprecations on class, method and function
          - `#1875 <https://github.com/ansys/pyedb/pull/1875>`_

        * - Improve value usage
          - `#1881 <https://github.com/ansys/pyedb/pull/1881>`_

        * - Refactor and aligned pinpair model
          - `#1883 <https://github.com/ansys/pyedb/pull/1883>`_

        * - DotNet Primitive queries refactoring
          - `#1912 <https://github.com/ansys/pyedb/pull/1912>`_


`0.70.0 <https://github.com/ansys/pyedb/releases/tag/v0.70.0>`_ - March 11, 2026
================================================================================

.. tab-set::


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Install pyaedt with group tests inside folder
          - `#1898 <https://github.com/ansys/pyedb/pull/1898>`_


`0.70.0 <https://github.com/ansys/pyedb/releases/tag/v0.70.0>`_ - March 10, 2026
================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Physical merge
          - `#1830 <https://github.com/ansys/pyedb/pull/1830>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Bump actions/setup-python from 6.1.0 to 6.2.0
          - `#1772 <https://github.com/ansys/pyedb/pull/1772>`_, `#1890 <https://github.com/ansys/pyedb/pull/1890>`_

        * - Update jupytext requirement from <1.19,>=1.16.0 to >=1.16.0,<1.20
          - `#1779 <https://github.com/ansys/pyedb/pull/1779>`_

        * - Bump actions/upload-artifact from 6.0.0 to 7.0.0
          - `#1863 <https://github.com/ansys/pyedb/pull/1863>`_, `#1876 <https://github.com/ansys/pyedb/pull/1876>`_

        * - Bump actions/download-artifact from 7.0.0 to 8.0.0
          - `#1864 <https://github.com/ansys/pyedb/pull/1864>`_

        * - Bump ansys/actions from 10.2.4 to 10.2.7
          - `#1865 <https://github.com/ansys/pyedb/pull/1865>`_, `#1877 <https://github.com/ansys/pyedb/pull/1877>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Adding DJ model docstring with add method
          - `#1847 <https://github.com/ansys/pyedb/pull/1847>`_

        * - Clean dotnet database geometry
          - `#1855 <https://github.com/ansys/pyedb/pull/1855>`_

        * - Reverting .NET documentation
          - `#1861 <https://github.com/ansys/pyedb/pull/1861>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Unittest
          - `#1826 <https://github.com/ansys/pyedb/pull/1826>`_

        * - Syntax issues
          - `#1837 <https://github.com/ansys/pyedb/pull/1837>`_

        * - Configuration.py
          - `#1845 <https://github.com/ansys/pyedb/pull/1845>`_

        * - Insert layout component
          - `#1869 <https://github.com/ansys/pyedb/pull/1869>`_

        * - Fixed 2 tests in grpc
          - `#1870 <https://github.com/ansys/pyedb/pull/1870>`_

        * - Cfg tests 2026.1 fix
          - `#1873 <https://github.com/ansys/pyedb/pull/1873>`_

        * - Hfss simulation setup grpc
          - `#1874 <https://github.com/ansys/pyedb/pull/1874>`_

        * - Test robustness
          - `#1882 <https://github.com/ansys/pyedb/pull/1882>`_

        * - Grpc cfg layer stackup test fix
          - `#1884 <https://github.com/ansys/pyedb/pull/1884>`_

        * - Downloads features
          - `#1885 <https://github.com/ansys/pyedb/pull/1885>`_

        * - Rf lib fixed
          - `#1886 <https://github.com/ansys/pyedb/pull/1886>`_

        * - RaptorX + HFSS-PI fixed and refactoring after edb-core changes
          - `#1888 <https://github.com/ansys/pyedb/pull/1888>`_

        * - Test_drc_rules_from_file_grpc_fixed
          - `#1889 <https://github.com/ansys/pyedb/pull/1889>`_

        * - Place 3dcomp and 3dlcomp
          - `#1896 <https://github.com/ansys/pyedb/pull/1896>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update CHANGELOG for v0.69.0
          - `#1825 <https://github.com/ansys/pyedb/pull/1825>`_

        * - Bump release 0.70.dev0
          - `#1827 <https://github.com/ansys/pyedb/pull/1827>`_

        * - Clean up root level files
          - `#1836 <https://github.com/ansys/pyedb/pull/1836>`_

        * - Group test dependencies
          - `#1840 <https://github.com/ansys/pyedb/pull/1840>`_

        * - Pre-commit automatic update
          - `#1844 <https://github.com/ansys/pyedb/pull/1844>`_, `#1879 <https://github.com/ansys/pyedb/pull/1879>`_, `#1894 <https://github.com/ansys/pyedb/pull/1894>`_

        * - Split into multiple workflows and clean up
          - `#1856 <https://github.com/ansys/pyedb/pull/1856>`_

        * - Add dependabot cooldown settings
          - `#1868 <https://github.com/ansys/pyedb/pull/1868>`_

        * - Rework main workflow to only build doc and upload dev docs
          - `#1887 <https://github.com/ansys/pyedb/pull/1887>`_

        * - Removing IDE warnings and fixing minor issues
          - `#1891 <https://github.com/ansys/pyedb/pull/1891>`_

        * - Update code owners
          - `#1892 <https://github.com/ansys/pyedb/pull/1892>`_

        * - Add codacy configuration file and badge
          - `#1893 <https://github.com/ansys/pyedb/pull/1893>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Lazy import and dependency rework
          - `#1828 <https://github.com/ansys/pyedb/pull/1828>`_

        * - Constants alignment between grpc dotnet
          - `#1829 <https://github.com/ansys/pyedb/pull/1829>`_

        * - Em properties
          - `#1842 <https://github.com/ansys/pyedb/pull/1842>`_

        * - Grpc warning messages added -> default DotNet
          - `#1846 <https://github.com/ansys/pyedb/pull/1846>`_

        * - Refactor grpc for configuration enablement
          - `#1857 <https://github.com/ansys/pyedb/pull/1857>`_

        * - XML control file unification
          - `#1866 <https://github.com/ansys/pyedb/pull/1866>`_

        * - Get_primitives
          - `#1867 <https://github.com/ansys/pyedb/pull/1867>`_

        * - Clean modeler
          - `#1872 <https://github.com/ansys/pyedb/pull/1872>`_

        * - Add deprecations on class, method and function
          - `#1875 <https://github.com/ansys/pyedb/pull/1875>`_

        * - Improve value usage
          - `#1881 <https://github.com/ansys/pyedb/pull/1881>`_

        * - Refactor and aligned pinpair model
          - `#1883 <https://github.com/ansys/pyedb/pull/1883>`_


`0.69.0 <https://github.com/ansys/pyedb/releases/tag/v0.69.0>`_ - February 11, 2026
===================================================================================

.. tab-set::


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update nbconvert requirement from <7.17 to <7.18
          - `#1814 <https://github.com/ansys/pyedb/pull/1814>`_

        * - Bump range upper bound for ansys-edb-core
          - `#1824 <https://github.com/ansys/pyedb/pull/1824>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Remove redundancies
          - `#1819 <https://github.com/ansys/pyedb/pull/1819>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update CHANGELOG for v0.68.3
          - `#1817 <https://github.com/ansys/pyedb/pull/1817>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Conftest edb examples
          - `#1820 <https://github.com/ansys/pyedb/pull/1820>`_

        * - Save_as
          - `#1823 <https://github.com/ansys/pyedb/pull/1823>`_


`0.68.3 <https://github.com/ansys/pyedb/releases/tag/v0.68.3>`_ - February 06, 2026
===================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - HFSS REGION
          - `#1813 <https://github.com/ansys/pyedb/pull/1813>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Issue#1800 #1810
          - `#1811 <https://github.com/ansys/pyedb/pull/1811>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update CHANGELOG for v0.68.2
          - `#1808 <https://github.com/ansys/pyedb/pull/1808>`_


`0.68.2 <https://github.com/ansys/pyedb/releases/tag/v0.68.2>`_ - February 04, 2026
===================================================================================

.. tab-set::


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Bump ansys/actions from 10.2.3 to 10.2.4
          - `#1786 <https://github.com/ansys/pyedb/pull/1786>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Mapping nap file with Edb grpc
          - `#1790 <https://github.com/ansys/pyedb/pull/1790>`_

        * - Edb cfg freq sweep typos
          - `#1797 <https://github.com/ansys/pyedb/pull/1797>`_

        * - Class MultiFrequencyAdaptSolution grpc
          - `#1798 <https://github.com/ansys/pyedb/pull/1798>`_

        * - CFG use Q3D for DC
          - `#1799 <https://github.com/ansys/pyedb/pull/1799>`_

        * - CFG setup minor
          - `#1801 <https://github.com/ansys/pyedb/pull/1801>`_

        * - Raptor fix
          - `#1804 <https://github.com/ansys/pyedb/pull/1804>`_

        * - Issue #1803 fix
          - `#1805 <https://github.com/ansys/pyedb/pull/1805>`_

        * - #1800 fix
          - `#1806 <https://github.com/ansys/pyedb/pull/1806>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update CHANGELOG for v0.68.0
          - `#1781 <https://github.com/ansys/pyedb/pull/1781>`_

        * - Bump release 0.69.0
          - `#1782 <https://github.com/ansys/pyedb/pull/1782>`_

        * - Update missing or outdated files
          - `#1795 <https://github.com/ansys/pyedb/pull/1795>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Removing cfg file 1.0 test and deprecating entire class.
          - `#1783 <https://github.com/ansys/pyedb/pull/1783>`_

        * - Test_edb_materials.py
          - `#1802 <https://github.com/ansys/pyedb/pull/1802>`_


`0.68.0 <https://github.com/ansys/pyedb/releases/tag/v0.68.0>`_ - January 27, 2026
==================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - XML Parser - stackup and nets
          - `#1774 <https://github.com/ansys/pyedb/pull/1774>`_

        * - Grpc simulation setup refactoring
          - `#1776 <https://github.com/ansys/pyedb/pull/1776>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Bump actions/checkout from 6.0.1 to 6.0.2
          - `#1775 <https://github.com/ansys/pyedb/pull/1775>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update gRPC message.
          - `#1773 <https://github.com/ansys/pyedb/pull/1773>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update CHANGELOG for v0.67.3
          - `#1770 <https://github.com/ansys/pyedb/pull/1770>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Terminal post processing
          - `#1756 <https://github.com/ansys/pyedb/pull/1756>`_

        * - Cfg setup enhancement
          - `#1771 <https://github.com/ansys/pyedb/pull/1771>`_

        * - Renaming grpc import
          - `#1780 <https://github.com/ansys/pyedb/pull/1780>`_


`0.67.3 <https://github.com/ansys/pyedb/releases/tag/v0.67.3>`_ - January 21, 2026
==================================================================================

.. tab-set::


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Grpc wave port tests resurrected
          - `#1761 <https://github.com/ansys/pyedb/pull/1761>`_

        * - Grpc source bug fix + consolidation
          - `#1763 <https://github.com/ansys/pyedb/pull/1763>`_

        * - Grpc layers consolidation
          - `#1764 <https://github.com/ansys/pyedb/pull/1764>`_

        * - Create port from padstack instance name bug fix
          - `#1765 <https://github.com/ansys/pyedb/pull/1765>`_

        * - Sweep property
          - `#1769 <https://github.com/ansys/pyedb/pull/1769>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update CHANGELOG for v0.67.1
          - `#1759 <https://github.com/ansys/pyedb/pull/1759>`_

        * - Bump_release_0.68.dev0
          - `#1760 <https://github.com/ansys/pyedb/pull/1760>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Edb cfg setup dotnet only
          - `#1766 <https://github.com/ansys/pyedb/pull/1766>`_


`0.67.1 <https://github.com/ansys/pyedb/releases/tag/v0.67.1>`_ - January 16, 2026
==================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Wirebond def management added
          - `#1746 <https://github.com/ansys/pyedb/pull/1746>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Extend troubleshooting with uv venv on Windows
          - `#1754 <https://github.com/ansys/pyedb/pull/1754>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Test modifying edb test file fixed
          - `#1750 <https://github.com/ansys/pyedb/pull/1750>`_

        * - Terminal hfss type
          - `#1757 <https://github.com/ansys/pyedb/pull/1757>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update CHANGELOG for v0.67.0
          - `#1747 <https://github.com/ansys/pyedb/pull/1747>`_

        * - Codecov component model
          - `#1751 <https://github.com/ansys/pyedb/pull/1751>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Source excitation
          - `#1744 <https://github.com/ansys/pyedb/pull/1744>`_

        * - Ide error fix
          - `#1748 <https://github.com/ansys/pyedb/pull/1748>`_

        * - Add dependency xmltodict
          - `#1752 <https://github.com/ansys/pyedb/pull/1752>`_

        * - Edb cfg cutout arguments
          - `#1753 <https://github.com/ansys/pyedb/pull/1753>`_

        * - Edb_object replaced by core
          - `#1755 <https://github.com/ansys/pyedb/pull/1755>`_


`0.67.0 <https://github.com/ansys/pyedb/releases/tag/v0.67.0>`_ - January 12, 2026
==================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Generate auto hfss regions
          - `#1714 <https://github.com/ansys/pyedb/pull/1714>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Bump actions/checkout from 6.0.0 to 6.0.1
          - `#1696 <https://github.com/ansys/pyedb/pull/1696>`_

        * - Bump ansys/actions from 10.1.5 to 10.2.2
          - `#1697 <https://github.com/ansys/pyedb/pull/1697>`_

        * - Update ansys-edb-core requirement from <0.2.3,>=0.2.0 to >=0.2.0,<0.2.4
          - `#1700 <https://github.com/ansys/pyedb/pull/1700>`_

        * - Bump codecov/codecov-action from 5.5.1 to 5.5.2
          - `#1705 <https://github.com/ansys/pyedb/pull/1705>`_

        * - Bump actions/download-artifact from 6.0.0 to 7.0.0
          - `#1708 <https://github.com/ansys/pyedb/pull/1708>`_

        * - Bump ansys/actions from 10.2.2 to 10.2.3
          - `#1720 <https://github.com/ansys/pyedb/pull/1720>`_

        * - Update pytest requirement from <8.5,>=7.4.0 to >=7.4.0,<9.1
          - `#1733 <https://github.com/ansys/pyedb/pull/1733>`_

        * - Update sphinx requirement from <8.3,>=7.1.0 to >=7.1.0,<9.1
          - `#1734 <https://github.com/ansys/pyedb/pull/1734>`_

        * - Bump numpydoc from 1.5.0 to 1.10.0
          - `#1735 <https://github.com/ansys/pyedb/pull/1735>`_

        * - Update sphinx-gallery requirement from <0.20,>=0.14.0 to >=0.14.0,<0.21
          - `#1736 <https://github.com/ansys/pyedb/pull/1736>`_

        * - Bump ansys-api-edb to 0.2.5
          - `#1743 <https://github.com/ansys/pyedb/pull/1743>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Change PyEDB documentation style
          - `#1721 <https://github.com/ansys/pyedb/pull/1721>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Reuse terminal
          - `#1738 <https://github.com/ansys/pyedb/pull/1738>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update CHANGELOG for v0.66.0
          - `#1712 <https://github.com/ansys/pyedb/pull/1712>`_

        * - Bump release 0.67.dev0
          - `#1715 <https://github.com/ansys/pyedb/pull/1715>`_

        * - Fix \`\`zizmor\`\` warnings in relation with \`\`ansys/actions/check-actions-security\`\` action
          - `#1723 <https://github.com/ansys/pyedb/pull/1723>`_

        * - Update CHANGELOG for v0.66.1
          - `#1732 <https://github.com/ansys/pyedb/pull/1732>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Remove cell from layout.py
          - `#1713 <https://github.com/ansys/pyedb/pull/1713>`_

        * - Dependencies updated
          - `#1716 <https://github.com/ansys/pyedb/pull/1716>`_

        * - Edb core refactoring
          - `#1717 <https://github.com/ansys/pyedb/pull/1717>`_

        * - Edb grpc main class warning fix
          - `#1729 <https://github.com/ansys/pyedb/pull/1729>`_

        * - Components refactoring
          - `#1740 <https://github.com/ansys/pyedb/pull/1740>`_

        * - Hfss refactoring
          - `#1741 <https://github.com/ansys/pyedb/pull/1741>`_


`0.66.1 <https://github.com/ansys/pyedb/releases/tag/v0.66.1>`_ - January 06, 2026
==================================================================================

.. tab-set::


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update test path and extend with other tests
          - `#1731 <https://github.com/ansys/pyedb/pull/1731>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Fix type hints and code warnings in padstacks.py
          - `#1726 <https://github.com/ansys/pyedb/pull/1726>`_


`0.66.1 <https://github.com/ansys/pyedb/releases/tag/v0.66.1>`_ - January 01, 2026
==================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Generate auto hfss regions
          - `#1714 <https://github.com/ansys/pyedb/pull/1714>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Bump actions/checkout from 6.0.0 to 6.0.1
          - `#1696 <https://github.com/ansys/pyedb/pull/1696>`_

        * - Bump ansys/actions from 10.1.5 to 10.2.2
          - `#1697 <https://github.com/ansys/pyedb/pull/1697>`_

        * - Update ansys-edb-core requirement from <0.2.3,>=0.2.0 to >=0.2.0,<0.2.4
          - `#1700 <https://github.com/ansys/pyedb/pull/1700>`_

        * - Bump codecov/codecov-action from 5.5.1 to 5.5.2
          - `#1705 <https://github.com/ansys/pyedb/pull/1705>`_

        * - Bump actions/download-artifact from 6.0.0 to 7.0.0
          - `#1708 <https://github.com/ansys/pyedb/pull/1708>`_

        * - Bump ansys/actions from 10.2.2 to 10.2.3
          - `#1720 <https://github.com/ansys/pyedb/pull/1720>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Change PyEDB documentation style
          - `#1721 <https://github.com/ansys/pyedb/pull/1721>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update CHANGELOG for v0.66.0
          - `#1712 <https://github.com/ansys/pyedb/pull/1712>`_

        * - Bump release 0.67.dev0
          - `#1715 <https://github.com/ansys/pyedb/pull/1715>`_

        * - Fix \`\`zizmor\`\` warnings in relation with \`\`ansys/actions/check-actions-security\`\` action
          - `#1723 <https://github.com/ansys/pyedb/pull/1723>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Remove cell from layout.py
          - `#1713 <https://github.com/ansys/pyedb/pull/1713>`_

        * - Dependencies updated
          - `#1716 <https://github.com/ansys/pyedb/pull/1716>`_

        * - Edb core refactoring
          - `#1717 <https://github.com/ansys/pyedb/pull/1717>`_


`0.66.0 <https://github.com/ansys/pyedb/releases/tag/v0.66.0>`_ - December 19, 2025
===================================================================================

.. tab-set::


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Bump actions/upload-artifact from 5.0.0 to 6.0.0
          - `#1707 <https://github.com/ansys/pyedb/pull/1707>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Fix typo in AUTHORS
          - `#1695 <https://github.com/ansys/pyedb/pull/1695>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Fixing static folder creation
          - `#1711 <https://github.com/ansys/pyedb/pull/1711>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Bump release 0.66.dev0
          - `#1682 <https://github.com/ansys/pyedb/pull/1682>`_

        * - Update CHANGELOG for v0.65.1
          - `#1684 <https://github.com/ansys/pyedb/pull/1684>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Component_def refactoring
          - `#1686 <https://github.com/ansys/pyedb/pull/1686>`_

        * - Material refactoring
          - `#1688 <https://github.com/ansys/pyedb/pull/1688>`_

        * - Nport component def refactoring
          - `#1689 <https://github.com/ansys/pyedb/pull/1689>`_

        * - Package def refactoring
          - `#1690 <https://github.com/ansys/pyedb/pull/1690>`_

        * - Edb cfg padstacks
          - `#1692 <https://github.com/ansys/pyedb/pull/1692>`_

        * - Random failure test
          - `#1694 <https://github.com/ansys/pyedb/pull/1694>`_

        * - Move control_file.py to generic folder
          - `#1701 <https://github.com/ansys/pyedb/pull/1701>`_

        * - Edb configure terminal
          - `#1702 <https://github.com/ansys/pyedb/pull/1702>`_

        * - Configure cfg_padstacks.py
          - `#1703 <https://github.com/ansys/pyedb/pull/1703>`_

        * - EDB CFG cutout
          - `#1706 <https://github.com/ansys/pyedb/pull/1706>`_

        * - Removing edb-core inheritance
          - `#1710 <https://github.com/ansys/pyedb/pull/1710>`_


`0.65.1 <https://github.com/ansys/pyedb/releases/tag/v0.65.1>`_ - November 27, 2025
===================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Insert 3d layout gRPC
          - `#1667 <https://github.com/ansys/pyedb/pull/1667>`_

        * - Place layout component enhancement
          - `#1680 <https://github.com/ansys/pyedb/pull/1680>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Working fine on local reverting test on grpc and cicd to check
          - `#1664 <https://github.com/ansys/pyedb/pull/1664>`_

        * - GRPC boundaries
          - `#1670 <https://github.com/ansys/pyedb/pull/1670>`_

        * - Remove try-except from property position
          - `#1679 <https://github.com/ansys/pyedb/pull/1679>`_

        * - Remove LD_LIBRARY_PATH need
          - `#1683 <https://github.com/ansys/pyedb/pull/1683>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update CHANGELOG for v0.65.0
          - `#1681 <https://github.com/ansys/pyedb/pull/1681>`_


`0.65.0 <https://github.com/ansys/pyedb/releases/tag/v0.65.0>`_ - November 27, 2025
===================================================================================

.. tab-set::


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Bump actions/checkout from 5.0.1 to 6.0.0
          - `#1665 <https://github.com/ansys/pyedb/pull/1665>`_

        * - Bump actions/setup-python from 6.0.0 to 6.1.0
          - `#1674 <https://github.com/ansys/pyedb/pull/1674>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Fixing hatched ground plane bug with grpc
          - `#1675 <https://github.com/ansys/pyedb/pull/1675>`_

        * - Issue 1621 fix
          - `#1677 <https://github.com/ansys/pyedb/pull/1677>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update CHANGELOG for v0.64.1
          - `#1669 <https://github.com/ansys/pyedb/pull/1669>`_


`0.64.1 <https://github.com/ansys/pyedb/releases/tag/v0.64.1>`_ - November 24, 2025
===================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Add grpc padstack instance bounding box property
          - `#1642 <https://github.com/ansys/pyedb/pull/1642>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Bump actions/checkout from 5.0.0 to 5.0.1
          - `#1655 <https://github.com/ansys/pyedb/pull/1655>`_

        * - Update jupyterlab requirement from <4.5,>=4.0.0 to >=4.0.0,<4.6
          - `#1656 <https://github.com/ansys/pyedb/pull/1656>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Remove JobManager from Edb class
          - `#1657 <https://github.com/ansys/pyedb/pull/1657>`_

        * - Fixing hfss extent
          - `#1660 <https://github.com/ansys/pyedb/pull/1660>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update CHANGELOG for v0.64.0
          - `#1652 <https://github.com/ansys/pyedb/pull/1652>`_

        * - Bump dev version into v0.65.dev0
          - `#1653 <https://github.com/ansys/pyedb/pull/1653>`_

        * - Delete accidentally added files
          - `#1661 <https://github.com/ansys/pyedb/pull/1661>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Edb cfg boundaries
          - `#1659 <https://github.com/ansys/pyedb/pull/1659>`_

        * - Add docstring to edb cfg boundaries
          - `#1663 <https://github.com/ansys/pyedb/pull/1663>`_


`0.64.0 <https://github.com/ansys/pyedb/releases/tag/v0.64.0>`_ - November 13, 2025
===================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Adding CLI for batch submission
          - `#1635 <https://github.com/ansys/pyedb/pull/1635>`_

        * - Job manager concurrent job bug
          - `#1640 <https://github.com/ansys/pyedb/pull/1640>`_

        * - Siwave log parser
          - `#1646 <https://github.com/ansys/pyedb/pull/1646>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Bump ansys/actions from 10.1.4 to 10.1.5
          - `#1623 <https://github.com/ansys/pyedb/pull/1623>`_

        * - Update pypandoc requirement from <1.16,>=1.10.0 to >=1.10.0,<1.17
          - `#1643 <https://github.com/ansys/pyedb/pull/1643>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Introduce \`\`sphinx-autoapi\`\` for API documentation
          - `#1632 <https://github.com/ansys/pyedb/pull/1632>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Bux fixed
          - `#1626 <https://github.com/ansys/pyedb/pull/1626>`_

        * - Create port on component (grpc) bug fixed
          - `#1628 <https://github.com/ansys/pyedb/pull/1628>`_

        * - Cfg_ports_sources.py
          - `#1644 <https://github.com/ansys/pyedb/pull/1644>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update CHANGELOG for v0.63.0
          - `#1624 <https://github.com/ansys/pyedb/pull/1624>`_

        * - Bump release 0.64.dev0
          - `#1634 <https://github.com/ansys/pyedb/pull/1634>`_

        * - Leverage new \`\`vtk-osmesa\`\` logic in CI
          - `#1651 <https://github.com/ansys/pyedb/pull/1651>`_


`0.63.0 <https://github.com/ansys/pyedb/releases/tag/v0.63.0>`_ - November 03, 2025
===================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Hatched ground plane with angle support
          - `#1620 <https://github.com/ansys/pyedb/pull/1620>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update CHANGELOG for v0.62.0
          - `#1614 <https://github.com/ansys/pyedb/pull/1614>`_

        * - Run PyAEDT test with PYAEDT_LOCAL_SETTINGS_PATH env var
          - `#1622 <https://github.com/ansys/pyedb/pull/1622>`_


`0.62.0 <https://github.com/ansys/pyedb/releases/tag/v0.62.0>`_ - October 28, 2025
==================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Add functionality for geometry swapping from DXF file
          - `#1529 <https://github.com/ansys/pyedb/pull/1529>`_

        * - Adding DRC inside pyedb
          - `#1600 <https://github.com/ansys/pyedb/pull/1600>`_

        * - Layout file warnings
          - `#1602 <https://github.com/ansys/pyedb/pull/1602>`_

        * - Design mode
          - `#1607 <https://github.com/ansys/pyedb/pull/1607>`_

        * - Job manager lsf support
          - `#1609 <https://github.com/ansys/pyedb/pull/1609>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Bump actions/labeler from 5.0.0 to 6.0.1
          - `#1578 <https://github.com/ansys/pyedb/pull/1578>`_

        * - Bump actions/download-artifact from 5.0.0 to 6.0.0
          - `#1610 <https://github.com/ansys/pyedb/pull/1610>`_

        * - Bump actions/upload-artifact from 4.6.2 to 5.0.0
          - `#1611 <https://github.com/ansys/pyedb/pull/1611>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Add the changelog feature
          - `#1593 <https://github.com/ansys/pyedb/pull/1593>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Job manager default values
          - `#1597 <https://github.com/ansys/pyedb/pull/1597>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Adding artifact attestations and fix warnings related to coverage upload
          - `#1601 <https://github.com/ansys/pyedb/pull/1601>`_


.. vale on


Changelog
=========

All notable changes to PyEDB are documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

[Unreleased]
------------
### Added
-

### Changed
-

### Deprecated
-

### Fixed
-

### Removed
-

[0.9.0] - 2024-XX-YY
--------------------
### Added
- Initial release of the gRPC-based PyEDB client.
- Comprehensive documentation including user guides, migration guide, and examples.
- Core functionality for EDB creation, modification, and simulation setup.

### Removed
- Legacy `pyedb.dotnet` module (moved to archived branch).