from abc import ABC
from enum import StrEnum
from typing import Annotated, Dict, Literal, Optional, Tuple

from pydantic import BaseModel, Discriminator


class ImpersonationExchangeType(StrEnum):
    REQUEST = "REQUEST"
    RESPONSE = "RESPONSE"
    INTERACT = "INTERACT"


class ImpersonationExchangeBase(BaseModel, ABC): ...


class ImpersonationExchangeInteract(ImpersonationExchangeBase):
    event: Literal[ImpersonationExchangeType.INTERACT] = ImpersonationExchangeType.INTERACT

    ws_url: str
    gui_url: Optional[str]


class ImpersonationExchangeRequest(ImpersonationExchangeBase):
    event: Literal[ImpersonationExchangeType.REQUEST] = ImpersonationExchangeType.REQUEST

    url: str
    method: str
    headers: Dict[str, str]
    body: Optional[bytes] = None


class ImpersonationExchangeResponse(ImpersonationExchangeBase):
    event: Literal[ImpersonationExchangeType.RESPONSE] = ImpersonationExchangeType.RESPONSE

    request: ImpersonationExchangeRequest

    url: str
    ok: bool
    status: int
    status_text: str
    headers: Dict[str, str]
    body: Optional[bytes] = None


ImpersonationExchange = Annotated[
    Tuple[
        ImpersonationExchangeRequest,
        ImpersonationExchangeResponse,
    ],
    Discriminator("event"),
]
