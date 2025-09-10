from pydantic import BaseModel, Field

from typing import Optional, List
from tortoise import models, fields
from tortoise.contrib.pydantic import pydantic_model_creator
from api.models.session import Session
from api.models.player import Player
# from api.schemas.player import 

GetSession = pydantic_model_creator(Session, name="session")


class PostSession(BaseModel):
    session_id: int
    active: bool
    board: Optional[Optional[int]]=None
    # player: List[GetPlayer]



class PutSession(BaseModel):
    active: bool
    board: Optional[Optional[int]]=None
    # player: List[GetPlayer]