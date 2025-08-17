import urllib
from contextlib import contextmanager
from typing import Generator, Literal, Optional, override

from playwright.sync_api import sync_playwright
from pydantic import AnyUrl, BaseModel, Field

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


class CDPGUIService(BaseModel):
    """
    A minimal client for Browserless's session API.
    """

    base_url: AnyUrl  # e.g. "https://browserless-gui.matthewcoulter.dev"

    def with_ws(self, ws: str) -> str:
        """
        Applies a ws url to the gui, ensuring the client can see that particular browser session
        """
        encoded_ws = urllib.parse.quote(ws, safe="")
        return f"{self.base_url}?ws={encoded_ws}"


class PlaywrightCDPImpersonator(PlaywrightImpersonatorBase):
    """Automate browser login to capture auth code via OIDC with PKCE. Good For CLIs, but"""

    tool: Literal[ImpersonatorTool.PLAYWRIGHT_CDP] = ImpersonatorTool.PLAYWRIGHT_CDP

    cdp_endpoint: str = Field(
        ...,
        description='CDP endpoint URL, e.g. "wss://your-browserless/chromium?token=..."',
    )
    cdp_headers: Optional[dict] = Field(default=None)
    cdp_timeout: Optional[float] = Field(default=None)
    cdp_gui_service: Optional[CDPGUIService] = None

    @contextmanager
    @override
    def init_context(
        self,
        url: str,
    ) -> Generator[PlaywrightContext, None, None]:
        # Note: no more p.chromium.launch(...)
        with sync_playwright() as p:
            # Connect to the remote Chrome running at localhost:9222
            browser = p.chromium.connect_over_cdp(
                self.cdp_endpoint,
                timeout=self.cdp_timeout,
                headers=self.cdp_headers,
            )
            # Create a new isolated context (cookies, cache, etc.)
            context = browser.new_context()
            page = context.new_page()
            page.goto(url)
            page.wait_for_load_state("networkidle")
            try:
                yield PlaywrightContext(
                    browser=browser,
                    context=context,
                    page=page,
                )
            finally:
                # This will disconnect Playwright, not shut down the container
                browser.close()

    @override
    def init_interaction(
        self,
        context: PlaywrightContext,
    ) -> Optional[ImpersonationExchangeInteract]:
        return None  # browser opens in client, no interaction preparation needed
