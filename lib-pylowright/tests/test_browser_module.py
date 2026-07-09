import importlib


def test_browser_module_exists_and_exposes_public_symbols():
    browser_module = importlib.import_module("pylowright.browser.browser")

    assert "BrowserSession" in browser_module.__all__
    assert "Browser" in browser_module.__all__
