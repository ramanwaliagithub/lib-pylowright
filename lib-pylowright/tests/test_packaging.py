import importlib
import pathlib


def test_package_imports():
    package = importlib.import_module("pylowright")
    assert package is not None


def test_version_file_exists():
    version_file = pathlib.Path(__file__).resolve().parents[1] / "pylowright" / "version.txt"
    assert version_file.exists()
