from contextlib import contextmanager
from typing import (
    Callable,
    Generator,
    Literal,
    Optional,
    override,
)

from ab_core.impersonation.schema.impersonation_exchange import (
    ImpersonationExchangeInteract,
    ImpersonationExchangeRequest,
    ImpersonationExchangeResponse,
)
from ab_core.impersonation.schema.impersonation_tool import (
    ImpersonatorTool,
)

from .base import ImpersonatorBase


class TemplateContext: ...


class TemplateImpersonator(ImpersonatorBase[TemplateContext]):
    """Automate browser login to capture auth code via OIDC with PKCE."""

    tool: Literal[ImpersonatorTool.TEMPLATE] = ImpersonatorTool.TEMPLATE

    @contextmanager
    @override
    def init_context(
        self,
        url: str,
    ) -> Generator[TemplateContext, None, None]:
        raise NotImplementedError()

    @override
    def init_interaction(
        self,
        context: TemplateContext,
    ) -> Optional[ImpersonationExchangeInteract]:
        raise NotImplementedError()

    @contextmanager
    @override
    def make_request(
        self,
        context: TemplateContext,
        request: ImpersonationExchangeRequest,
    ) -> Generator[ImpersonationExchangeResponse, None, None]:
        raise NotImplementedError()

    @contextmanager
    @override
    def intercept_response(
        self,
        context: TemplateContext,
        cond: Callable[[ImpersonationExchangeResponse], bool],
        timeout: int,
    ) -> Generator[ImpersonationExchangeResponse, None, None]:
        raise NotImplementedError()
