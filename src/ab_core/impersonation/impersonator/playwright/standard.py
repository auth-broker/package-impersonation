from contextlib import contextmanager
from typing import Generator, Literal, Optional, override

from playwright.sync_api import sync_playwright

from ab_core.impersonation.schema.impersonation_exchange import (
    ImpersonationExchangeInteract,
)
from ab_core.impersonation.schema.impersonation_tool import (
    ImpersonatorTool,
)

from .base import (
    PlaywrightContext,
    PlaywrightImpersonatorBase,
)


class PlaywrightImpersonator(PlaywrightImpersonatorBase):
    """Automate browser login to capture auth code via OIDC with PKCE. Good For CLIs, but"""

    tool: Literal[ImpersonatorTool.PLAYWRIGHT] = ImpersonatorTool.PLAYWRIGHT
    browser_channel: str = "chrome"

    @contextmanager
    @override
    def init_context(
        self,
        url: str,
    ) -> Generator[PlaywrightContext, None, None]:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                channel=self.browser_channel,
                headless=False,
                args=["--disable-blink-features=AutomationControlled"],
            )
            context = browser.new_context()
            page = context.new_page()
            page.goto(url)
            try:
                yield PlaywrightContext(
                    context=context,
                    page=page,
                )
            finally:
                browser.close()

    @override
    def init_interaction(
        self,
        context: PlaywrightContext,
    ) -> Optional[ImpersonationExchangeInteract]:
        return None  # browser opens in client, no interaction preparation needed
