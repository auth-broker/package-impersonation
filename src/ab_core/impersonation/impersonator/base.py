from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import (
    Callable,
    Generator,
    Generic,
    Optional,
    TypeVar,
)

from pydantic import BaseModel

from ab_core.impersonation.schema.impersonation_exchange import (
    ImpersonationExchangeInteract,
    ImpersonationExchangeRequest,
    ImpersonationExchangeResponse,
)

T_CONTEXT = TypeVar("T_CONTEXT")


class ImpersonatorBase(BaseModel, Generic[T_CONTEXT], ABC):
    """Automate browser login to capture auth code via OIDC with PKCE."""

    @contextmanager
    @abstractmethod
    def init_context(
        self,
        url: str,
    ) -> Generator[T_CONTEXT, None, None]: ...

    @abstractmethod
    def init_interaction(
        self,
        context: T_CONTEXT,
    ) -> Optional[ImpersonationExchangeInteract]: ...

    @contextmanager
    @abstractmethod
    def make_request(
        self,
        context: T_CONTEXT,
        request: ImpersonationExchangeRequest,
    ) -> Generator[ImpersonationExchangeResponse, None, None]: ...

    @contextmanager
    @abstractmethod
    def intercept_response(
        self,
        context: T_CONTEXT,
        cond: Callable[[ImpersonationExchangeResponse], bool],
        timeout: int,
    ) -> Generator[ImpersonationExchangeResponse, None, None]: ...
