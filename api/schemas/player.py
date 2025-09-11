from pydantic import BaseModel, Field

from tortoise.contrib.pydantic import pydantic_model_creator
from api.models.player import Player
from api.models.session import Session
# from api.schemas.session import PostSession
        
GetPlayer = pydantic_model_creator(Player, name="player")


class PostPlayer(BaseModel):
    player_id: int
    name : str
    score : int
    steps: int
    session_id: int # have to input this for postman

class PutPlayer(BaseModel):
    name : str
    score : int
    steps: int
    session_id: int
