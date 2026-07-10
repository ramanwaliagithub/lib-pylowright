import importlib


def test_root_package_exports_public_api():
    pkg = importlib.import_module("pylowright")

    assert hasattr(pkg, "Browser")
    assert hasattr(pkg, "BrowserSession")
    assert hasattr(pkg, "start_browser")
    assert hasattr(pkg, "start_persistent_browser")
    assert hasattr(pkg, "__version__")
    assert pkg.__version__ == "0.4"
