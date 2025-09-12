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
    # session = await Session.get(session_id=player.session_id)
    # use player.session_id to get session, and check session's player number
    exists = await Player.filter(player_id=player.player_id).exists()
    if exists:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Player already existed")
    
    players = await Player.filter(session__session_id=player.session_id)
    if len(players) > 2:
        raise HTTPException(status.HTTP_406_NOT_ACCEPTABLE, detail=" The session is full, choose another one") 
    data = await Player.create(**player.model_dump())
    return await GetPlayer.from_tortoise_orm(data)
    

@player_router.put("/player/{player_id}")
async def update_player(player_id: int, body: PutPlayer):
    data = body.model_dump()

    exists = await Player.filter(player_id=player_id).exists()

    if not exists:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Player Not Found")

    await Player.filter(player_id=player_id).update(**data)
    player = await GetPlayer.from_queryset_single(Player.get(player_id=player_id))
    
    return player

@player_router.delete("player/{player_id}")
async def delete_player(player_id: int):
    exists = await Player.filter(player_id=player_id).exists()

    if not exists:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Player Not Found")
    await Player.filter(player_id=player_id).delete()
    return f"The player {player_id} has been successfully deleted"