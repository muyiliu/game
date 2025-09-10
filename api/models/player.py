from tortoise import Model
from tortoise.fields import IntField, BooleanField, CharField

class Player(Model):
    player_id = IntField(pk=True)
    name = CharField(max_length=255)
    playing = BooleanField(default=False)
    score= IntField(default=0)