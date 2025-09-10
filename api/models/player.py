from tortoise import Model
from tortoise.fields import IntField, BooleanField, CharField, ForeignKeyRelation, CASCADE, ForeignKeyField

from api.models.session import Session


    
class Player(Model):
    player_id = IntField(pk=True)
    name = CharField(max_length=255)
    playing = BooleanField(default=False)
    score= IntField(default=0)
    session: ForeignKeyRelation[Session] = ForeignKeyField(
        "models.Session", related_name="players", on_delete=CASCADE
    )