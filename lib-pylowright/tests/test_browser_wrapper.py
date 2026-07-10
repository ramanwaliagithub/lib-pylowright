from pylowright.browser.browser import Browser
from pylowright.browser.session import BrowserSession, _Mode


class FakePage:
    def __init__(self) -> None:
        self.goto_calls = []
        self.wait_calls = []
        self._title = "Example"
        self._url = "about:blank"

    def goto(self, url: str, wait_until: str = "load") -> None:
        self.goto_calls.append((url, wait_until))
        self._url = url

    def wait_for_load_state(self, state: str = "load") -> None:
        self.wait_calls.append(state)

    @property
    def title(self) -> str:
        return self._title

    @property
    def url(self) -> str:
        return self._url


class FakeSession(BrowserSession):
    def __init__(self) -> None:
        self._mode = _Mode.EPHEMERAL
        self._page = FakePage()
        self._context = None
        self._playwright = None


def test_browser_wrapper_forwards_page_methods():
    session = FakeSession()
    browser = Browser(session)

    browser.goto("https://example.com")
    browser.wait_for_load_state("networkidle")

    assert browser.title == "Example"
    assert browser.url == "https://example.com"
    assert browser.page.goto_calls == [("https://example.com", "load")]
    assert browser.page.wait_calls == ["networkidle"]
