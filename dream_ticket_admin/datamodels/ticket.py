from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict


class TicketData(BaseModel):
    sync_id: Optional[int] = Field(serialization_alias="id", default=0)
    name: str
    description: Optional[str] = ""
    state: str
    start_num: int
    end_num: int
    win_num: Optional[int] = -1
    available_count: int
    reserved_count: int
    sold_count: int

    @classmethod
    def construct_from_gql(cls, data: Dict[str, Any]) -> "TicketData":
        return TicketData(
            sync_id=data.get("id"),
            name=data.get("name"),
            description=data.get("description"),
            state=data.get("state"),
            start_num=data.get("startNum"),
            end_num=data.get("endNum"),
            win_num=data.get("winNum"),
            available_count=data.get("availableCount"),
            reserved_count=data.get("reservedCount"),
            sold_count=data.get("soldCount"),
        )


class TicketLineData(BaseModel):
    special_price: float
    is_special_price: bool
    user_code: Optional[str]
    state: str
    number: int
    ticket_id: int
    sync_id: Optional[int] = Field(serialization_alias="id", default=0)

    @classmethod
    def construct_from_gql(cls, data: Dict[str, Any]) -> "TicketLineData":
        return TicketLineData(
            ticket_id=data.get("ticketId"),
            sync_id=data.get("id"),
            number=data.get("number"),
            state=data.get("state"),
            user_code=data.get("userCode"),
            is_special_price=data.get("isSpecialPrice"),
            special_price=data.get("specialPrice"),
        )
