from pydantic import BaseModel, Field

from typing import Annotated, Optional, List
from tortoise import models, fields
from tortoise.contrib.pydantic import pydantic_model_creator
from api.models.session import Session
from api.models.player import Player
from api.schemas.player import GetPlayer, PostPlayer
# from api.schemas.player import 

GetSession = pydantic_model_creator(Session, name="session")
# Each row must be exactly 3 ints
BoardRow = Annotated[list[int], Field(min_length=3, max_length=3)]
# Board must be exactly 3 rows
BoardType = Annotated[list[BoardRow], Field(min_length=3, max_length=3)]

PlayerList = Annotated[list[PostPlayer], Field(min_length=1, max_length=2)]

class PostSession(BaseModel):
    session_id: int
    active: bool
    board: BoardType
    # players: Optional[PlayerList]=None


class PutSession(BaseModel):
    active: bool
    board: Optional[BoardType]=None
    players: Optional[PlayerList]=None


class Move(BaseModel):
    player_id:int
    row: int
    col: int