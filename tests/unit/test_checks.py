# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

from unittest.mock import MagicMock, patch
import warnings

import pytest

from pyedb.internal import checks

pytestmark = [pytest.mark.unit, pytest.mark.no_licence]


@pytest.fixture(autouse=True)
def clear_dependency_cache():
    """Clear the dependency cache before and after each test."""
    checks._DEPENDENCY_CACHE.clear()
    yield
    checks._DEPENDENCY_CACHE.clear()


class TestInstallMessage:
    """Tests for install_message function."""

    def test_single_dependency_message(self):
        """Test install message for a single dependency."""
        msg = checks.install_message("pyvista", "graphics")
        assert "Dependency pyvista is required" in msg
        assert "Please install the ``graphics`` target" in msg
        assert "pip install pyedb[graphics]" in msg

    def test_multiple_dependencies_message(self):
        """Test install message for multiple dependencies."""
        msg = checks.install_message(["pyvista", "vtk", "matplotlib"], "graphics")
        assert "Dependencies pyvista, vtk, matplotlib are required" in msg
        assert "Please install the ``graphics`` target" in msg
        assert "pip install pyedb[graphics]" in msg

    def test_default_level_is_method(self):
        """Test that default level parameter is 'method'."""
        msg = checks.install_message("pyvista", "graphics")
        assert "use this method" in msg

    def test_custom_level_parameter(self):
        """Test custom level parameter in message."""
        msg = checks.install_message("pyvista", "graphics", level="function")
        assert "use this function" in msg

    def test_target_all_shows_different_message(self):
        """Test message for 'all' target shows different pip command."""
        msg = checks.install_message("pyvista", "all")
        assert "pip install pyedb[all]" in msg
        assert "or `pip install pyedb[all]`" not in msg

    def test_target_all_no_or_clause(self):
        """Test that 'all' target doesn't include 'or pip install pyedb[all]'."""
        msg = checks.install_message("pyvista", "all")
        assert msg.endswith(".")


class TestCheckDependency:
    """Tests for check_dependency function."""

    def test_available_dependency_returns_true(self):
        """Test that available dependency returns True."""
        result = checks.check_dependency("sys")
        assert result is True

    def test_available_dependency_caches_result(self):
        """Test that available dependency is cached."""
        checks.check_dependency("sys")
        assert checks._DEPENDENCY_CACHE.get("sys") is True

    def test_unavailable_dependency_raises_error(self):
        """Test that unavailable dependency raises ImportError."""
        with pytest.raises(ImportError) as exc_info:
            checks.check_dependency("nonexistent_module_xyz_12345", target="test")
        assert "Dependency nonexistent_module_xyz_12345 is required" in str(exc_info.value)

    def test_unavailable_dependency_caches_result(self):
        """Test that unavailable dependency is cached."""
        with pytest.raises(ImportError):
            checks.check_dependency("nonexistent_module_xyz_12345")
        assert checks._DEPENDENCY_CACHE.get("nonexistent_module_xyz_12345") is False

    def test_unavailable_dependency_with_warning_mode(self):
        """Test that unavailable dependency issues warning in warning mode."""
        with pytest.warns(UserWarning) as record:
            result = checks.check_dependency("nonexistent_module_xyz_12345", warning=True)
        assert result is False
        assert len(record) == 1
        assert "Dependency nonexistent_module_xyz_12345 is required" in str(record[0].message)

    def test_dependency_alias_pillow_to_pil(self):
        """Test that 'pillow' alias resolves to 'PIL'."""
        with patch("pyedb.internal.checks.import_module") as mock_import:
            mock_import.side_effect = ImportError("PIL not found")
            with pytest.raises(ImportError):
                checks.check_dependency("pillow")
            mock_import.assert_called_once_with("PIL")

    def test_dependency_alias_visualization_interface(self):
        """Test that 'visualization_interface' alias resolves correctly."""
        with patch("pyedb.internal.checks.import_module") as mock_import:
            mock_import.side_effect = ImportError("Module not found")
            with pytest.raises(ImportError):
                checks.check_dependency("visualization_interface")
            mock_import.assert_called_once_with("ansys.tools.visualization_interface")

    def test_dependency_alias_pythonnet(self):
        """Test that 'ansys-pythonnet' alias resolves to 'pythonnet'."""
        with patch("pyedb.internal.checks.import_module") as mock_import:
            mock_import.side_effect = ImportError("pythonnet not found")
            with pytest.raises(ImportError):
                checks.check_dependency("ansys-pythonnet")
            mock_import.assert_called_once_with("pythonnet")

    def test_dependency_no_alias_uses_name_directly(self):
        """Test that dependencies without aliases use their name directly."""
        with patch("pyedb.internal.checks.import_module") as mock_import:
            mock_import.side_effect = ImportError("Module not found")
            with pytest.raises(ImportError):
                checks.check_dependency("pyvista")
            mock_import.assert_called_once_with("pyvista")

    def test_custom_target_in_error_message(self):
        """Test that custom target appears in error message."""
        with pytest.raises(ImportError) as exc_info:
            checks.check_dependency("nonexistent_xyz", target="custom_target")
        assert "Please install the ``custom_target`` target" in str(exc_info.value)

    def test_cache_prevents_multiple_imports(self):
        """Test that cache prevents reimporting the same dependency."""
        with patch("pyedb.internal.checks.import_module") as mock_import:
            mock_import.return_value = MagicMock()
            checks.check_dependency("test_module")
            checks.check_dependency("test_module")
            mock_import.assert_called_once_with("test_module")

    def test_warning_does_not_raise_but_returns_false(self):
        """Test that warning mode doesn't raise but returns False."""
        result = checks.check_dependency("nonexistent_xyz_warning", warning=True)
        assert result is False

    def test_available_with_warning_still_returns_true(self):
        """Test that available dependency returns True even with warning=True."""
        result = checks.check_dependency("sys", warning=True)
        assert result is True


class TestRequiresDependencyDecorator:
    """Tests for _requires_dependency decorator factory."""

    def test_requires_dependency_no_dependencies_raises_error(self):
        """Test that providing no dependencies raises ValueError."""
        with pytest.raises(ValueError, match="At least one dependency must be provided"):
            checks._requires_dependency(target="test")

    def test_requires_dependency_creates_decorator(self):
        """Test that _requires_dependency returns a decorator."""
        decorator = checks._requires_dependency("sys", target="test")
        assert callable(decorator)

    def test_decorator_wraps_function(self):
        """Test that decorator properly wraps a function."""

        @checks._requires_dependency("sys", target="test")
        def dummy_func():
            return "result"

        result = dummy_func()
        assert result == "result"

    def test_decorator_checks_dependency_before_calling_function(self):
        """Test that decorator checks dependency before executing function."""

        @checks._requires_dependency("nonexistent_xyz", target="test")
        def dummy_func():
            return "should not reach here"

        with pytest.raises(ImportError):
            dummy_func()

    def test_decorator_with_multiple_dependencies(self):
        """Test decorator with multiple dependencies."""

        @checks._requires_dependency("sys", "os", target="test")
        def dummy_func():
            return "success"

        result = dummy_func()
        assert result == "success"

    def test_decorator_with_multiple_dependencies_fails_on_first_missing(self):
        """Test that decorator fails on first missing dependency."""

        @checks._requires_dependency("sys", "nonexistent_xyz", target="test")
        def dummy_func():
            return "should not reach"

        with pytest.raises(ImportError) as exc_info:
            dummy_func()
        assert "nonexistent_xyz" in str(exc_info.value)

    def test_decorator_passes_arguments_to_function(self):
        """Test that decorator passes arguments correctly."""

        @checks._requires_dependency("sys", target="test")
        def dummy_func(a, b, kwarg=None):
            return (a, b, kwarg)

        result = dummy_func(1, 2, kwarg=3)
        assert result == (1, 2, 3)

    def test_decorator_target_is_used_in_error_message(self):
        """Test that target parameter is included in error message."""

        @checks._requires_dependency("nonexistent_xyz", target="custom_target")
        def dummy_func():
            return "should not reach"

        with pytest.raises(ImportError) as exc_info:
            dummy_func()
        assert "custom_target" in str(exc_info.value)

    def test_decorator_preserves_function_name(self):
        """Test that decorator preserves function name with functools.wraps."""

        @checks._requires_dependency("sys", target="test")
        def my_special_function():
            return "result"

        assert my_special_function.__name__ == "my_special_function"

    def test_decorator_checks_all_dependencies(self):
        """Test that decorator checks all dependencies in order."""
        call_order = []

        def mock_check_dependency(dep, target):
            call_order.append(dep)
            if dep == "dep2":
                raise ImportError(f"Missing {dep}")

        with patch("pyedb.internal.checks.check_dependency", side_effect=mock_check_dependency):

            @checks._requires_dependency("dep1", "dep2", "dep3", target="test")
            def dummy_func():
                return "should not reach"

            with pytest.raises(ImportError):
                dummy_func()

        assert call_order == ["dep1", "dep2"]


class TestRequiresDotnetDependencyDecorator:
    """Tests for requires_dotnet_dependency decorator."""

    def test_requires_dotnet_dependency_returns_decorator(self):
        """Test that requires_dotnet_dependency returns a decorator."""
        decorator = checks.requires_dotnet_dependency("ansys-pythonnet")
        assert callable(decorator)

    def test_requires_dotnet_dependency_sets_target_to_dotnet(self):
        """Test that requires_dotnet_dependency sets target='dotnet'."""

        @checks.requires_dotnet_dependency("sys")
        def dummy_func():
            return "success"

        result = dummy_func()
        assert result == "success"

    def test_requires_dotnet_dependency_with_missing_dependency(self):
        """Test that missing dotnet dependency raises error with dotnet target."""

        @checks.requires_dotnet_dependency("nonexistent_xyz_dotnet")
        def dummy_func():
            return "should not reach"

        with pytest.raises(ImportError) as exc_info:
            dummy_func()
        assert "dotnet" in str(exc_info.value)
        assert "nonexistent_xyz_dotnet" in str(exc_info.value)

    def test_requires_dotnet_dependency_with_multiple_dependencies(self):
        """Test requires_dotnet_dependency with multiple dependencies."""

        @checks.requires_dotnet_dependency("sys", "os")
        def dummy_func():
            return "success"

        result = dummy_func()
        assert result == "success"

    def test_requires_dotnet_dependency_no_dependencies_raises_error(self):
        """Test that no dependencies raises ValueError."""
        with pytest.raises(ValueError, match="At least one dependency must be provided"):
            checks.requires_dotnet_dependency()


class TestDependencyCacheIntegration:
    """Integration tests for dependency caching."""

    def test_cache_shared_across_different_check_calls(self):
        """Test that cache is shared across different dependency check calls."""
        checks.check_dependency("sys")
        assert checks._DEPENDENCY_CACHE.get("sys") is True

        # Second call should use cache
        with patch("pyedb.internal.checks.import_module") as mock_import:
            checks.check_dependency("sys")
            mock_import.assert_not_called()

    def test_cache_independent_for_different_dependencies(self):
        """Test that different dependencies have independent cache entries."""
        checks.check_dependency("sys")
        checks._DEPENDENCY_CACHE["os"] = False

        assert checks._DEPENDENCY_CACHE.get("sys") is True
        assert checks._DEPENDENCY_CACHE.get("os") is False

    def test_mixed_available_and_unavailable_in_cache(self):
        """Test cache with mix of available and unavailable dependencies."""
        checks.check_dependency("sys")

        with pytest.raises(ImportError):
            checks.check_dependency("nonexistent_xyz_mixed")

        assert checks._DEPENDENCY_CACHE.get("sys") is True
        assert checks._DEPENDENCY_CACHE.get("nonexistent_xyz_mixed") is False
