# tests/test_browserless_impersonator.py

import pytest

from ab_core.impersonation.schema.impersonation_exchange import ImpersonationExchange
from ab_core.impersonation.impersonator.playwright.browserless import (  # ← adjust import path to your module
    PlaywrightCDPBrowserlessImpersonator,
)


@pytest.fixture
def config() -> dict:
    return {
        "tool": "PLAYWRIGHT_CDP_BROWSERLESS",
        "cdp_endpoint": "wss://browserless.matthewcoulter.dev/?stealth=true&blockAds=true&ignoreHTTPSErrors=true&timezoneId=Australia/Sydney",
        "cdp_headers": None,
        "cdp_timeout": None,
        "cdp_gui_service": {
            "base_url": "https://browserless-gui.matthewcoulter.dev/",
        },
        "browserless_service": {
            "base_url": "https://browserless.matthewcoulter.dev/",
            # the code now computes sessions_url/ws_url_prefix itself,
            # but these are here to mirror your provided structure
        },
    }


@pytest.fixture
def impersonator(config) -> PlaywrightCDPBrowserlessImpersonator:
    # Build the impersonator as your app would
    return PlaywrightCDPBrowserlessImpersonator.model_validate(config)


@pytest.mark.asyncio
async def test_interaction_async(impersonator: PlaywrightCDPBrowserlessImpersonator):
    async with impersonator.init_context_async("https://example.com/login") as context:
        # prepare the user interaction
        interaction = await impersonator.init_interaction_async(context)
        if interaction:
            # You need to open interaction.gui_url in your browser,
            # the click on Learn More in order for this test case to pass
            print(interaction)

        def is_on_domain_page(r: ImpersonationExchange):
            return r.url == "https://iana.org/domains/example" and r.status == 301

        # intercept the response during user interaction
        async with impersonator.intercept_async(
            context,
            event="response",
            cond=is_on_domain_page,
        ) as resp:
            assert resp.headers.get("location") == "https://iana.org/domains/example"