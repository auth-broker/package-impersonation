import logging
from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import field
from typing import (
    Any,
    Callable,
    Generator,
    Optional,
    TypeVar,
    override,
)

from playwright.sync_api import (
    Browser,
    BrowserContext,
    Page,
)
from pydantic import BaseModel
from uuid_extensions import uuid7

from ab_core.impersonation.schema.impersonation_exchange import (
    ImpersonationExchangeInteract,
    ImpersonationExchangeRequest,
    ImpersonationExchangeResponse,
)

from ..base import ImpersonatorBase

logger = logging.getLogger(__name__)


class PlaywrightContext(BaseModel):
    id: str = field(default_factory=lambda: str(uuid7()))

    browser: Browser
    context: BrowserContext
    page: Page

    class Config:
        arbitrary_types_allowed = True


PLAYWRIGHT_CONTEXT_T = TypeVar("PLAYWRIGHT_CONTEXT_T", bound=PlaywrightContext)


class PlaywrightImpersonatorBase(ImpersonatorBase[PLAYWRIGHT_CONTEXT_T], ABC):
    """Automate browser login to capture auth code via OIDC with PKCE. Good For CLIs, but"""

    @contextmanager
    @abstractmethod
    def init_context(
        self,
        url: str,
    ) -> Generator[PLAYWRIGHT_CONTEXT_T, None, None]: ...

    @abstractmethod
    def init_interaction(
        self,
        context: PLAYWRIGHT_CONTEXT_T,
    ) -> Optional[ImpersonationExchangeInteract]: ...

    @override
    def make_request(
        self,
        context: PLAYWRIGHT_CONTEXT_T,
        request: ImpersonationExchangeRequest,
    ) -> Generator[ImpersonationExchangeResponse, None, None]:
        api_request = context.context.request
        response = api_request.fetch(
            url=request.url,
            method=request.method,
            headers=request.headers,
            data=request.body,
        )
        yield self._cast_response(response)

    @contextmanager
    @override
    def intercept_response(
        self,
        context: PLAYWRIGHT_CONTEXT_T,
        cond: Callable[[ImpersonationExchangeResponse], bool],
        timeout: int,
    ) -> Generator[ImpersonationExchangeResponse, None, None]:
        playwright_event = context.context.wait_for_event(
            "response",
            lambda event: cond(self._cast_response(event)),
            timeout=timeout,
        )
        yield self._cast_response(playwright_event)

    def _cast_request(self, request: Any) -> ImpersonationExchangeRequest:
        return ImpersonationExchangeRequest(
            url=str(request.url),
            headers=dict(request.headers),
            body=request.post_data_buffer,
            method=request.method,
        )

    def _cast_response(self, response: Any) -> ImpersonationExchangeResponse:
        response_body = None
        try:
            response_body = response.body()
        except Exception as e:
            logger.warning(
                "Unable to read response body.",
                exc_info=e,
            )

        return ImpersonationExchangeResponse(
            request=self._cast_request(response.request),
            url=str(response.url),
            headers=dict(response.headers),
            body=response_body,
            ok=response.ok,
            status=response.status,
            status_text=response.status_text,
        )
