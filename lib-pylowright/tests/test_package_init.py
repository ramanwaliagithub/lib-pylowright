import importlib


def test_package_init_exposes_version_and_browser():
    package = importlib.import_module("pylowright")
    assert hasattr(package, "__version__")
    assert hasattr(package, "Browser")
    assert hasattr(package, "BrowserSession")
    assert hasattr(package, "start_browser")
    assert package.__version__ == "0.4"
