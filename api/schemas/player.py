from pydantic import BaseModel, Field

from typing import Optional
from tortoise import models, fields
from tortoise.contrib.pydantic import pydantic_model_creator
from api.models.player import Player
        
GetPlayer = pydantic_model_creator(Player, name="player")


class PostPlayer(BaseModel):
    player_id: int
    name : str
    playing : bool
    score : int


class PutPlayer(BaseModel):
    name : str
    playing : bool
    score : int


# {
#     "player_id": 1,
#     "name" : "Mu",
#     "playing" : true,
#     "score" : 0
# }