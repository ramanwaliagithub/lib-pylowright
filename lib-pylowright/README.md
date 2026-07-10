# pylowright

A lightweight browser automation helper package for Playwright-based browser automation.

## Installation

Install the package locally for development:

```bash
pip install -e .
```

Install runtime dependencies:

```bash
pip install playwright
playwright install
```

## Usage

Import the package and create a browser session using the provided APIs:

```python
from pylowright import Browser

browser = Browser.persistent(profile="chrome")
try:
    browser.goto("https://example.com")
    print(browser.title)
finally:
    browser.close()
```

Or use a session directly:

```python
from pylowright.browser import BrowserSession
from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    session = BrowserSession.ephemeral(pw.chromium, profile="chrome")
    session.goto("https://example.com")
    print(session.title)
    session.close()
```

## Testing

Run tests:

```bash
pytest -q
```
