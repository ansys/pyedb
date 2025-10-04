import os
from pathlib import Path
import subprocess
import sys


def build_ui():
    """Build the React UI"""
    ui_dir = Path(__file__).parent / "ui"

    if not ui_dir.exists():
        print(f"UI directory not found: {ui_dir}")
        return False

    print("Building React UI...")

    try:
        # Install dependencies
        print("Installing npm dependencies...")
        result = subprocess.run([r"C:\Program Files\nodejs\npm.cmd", "install"], cwd=ui_dir, check=True)

        if result.returncode != 0:
            print("Failed to install dependencies:")
            print(result.stderr)
            return False

        # Build the UI
        print("Building UI...")
        result = subprocess.run([r"C:\Program Files\nodejs\npm.cmd", "run", "build"], cwd=ui_dir, check=True)

        if result.returncode != 0:
            print("Build failed:")
            print(result.stderr)
            return False

        print("UI built successfully!")
        return True

    except Exception as e:
        print(f"Error building UI: {e}")
        return False


if __name__ == "__main__":
    build_ui()
