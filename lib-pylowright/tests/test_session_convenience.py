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


def test_session_wrappers_delegate_to_page():
    session = BrowserSession.deferred()
    session._mode = _Mode.EPHEMERAL
    page = FakePage()
    session._page = page

    session.goto("https://example.com")
    session.wait_for_load_state("networkidle")

    assert page.goto_calls == [("https://example.com", "load")]
    assert page.wait_calls == ["networkidle"]
    assert session.title == "Example"
    assert session.url == "https://example.com"
