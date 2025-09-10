from tortoise.models import Model
from tortoise.fields import IntField, BooleanField, CharField, JSONField, ReverseRelation

# from api.models.player import Player


def default_board():
    return [[0, 0, 0] for _ in range(3)]

class Session(Model):
    session_id = IntField(pk=True)
    active=BooleanField(default=False)
    board=JSONField(null=True, default=default_board)
    players=ReverseRelation["Player"]

