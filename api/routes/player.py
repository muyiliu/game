from fastapi import APIRouter, HTTPException,status
from api.models.player import Player

from api.schemas.player import GetPlayer, PostPlayer, PutPlayer

player_router = APIRouter(prefix="/api", tags=["player"])

# Following functions are Players
@player_router.get("/player")
async def all_player():
    data = Player.all()
    return await GetPlayer.from_queryset(data)

@player_router.post("/player")
async def post_player(player: PostPlayer):
    row = await Player.create(**player.model_dump())
    
    return await GetPlayer.from_tortoise_orm(row)

@player_router.put("/player/{player_id}")
async def update_player(player_id: int, body: PutPlayer):
    data = body.model_dump()

    exists = await Player.filter(player_id=player_id).exists()

    if not exists:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Player Not Found")

    await Player.filter(player_id=player_id).update(**data)
    player = await GetPlayer.from_queryset_single(Player.get(player_id=player_id))
    
    return player