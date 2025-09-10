from fastapi import APIRouter, HTTPException,status
from api.models.player import Player
from api.models.session import Session
from api.schemas.player import GetPlayer
from api.schemas.session import GetSession, PostSession, PutSession

session_router = APIRouter(prefix="/api", tags=["session"])

# For the following are routers for session
@session_router.get("/session")
async def all_session():
    data = Session.all()
    print(data)
    return await GetSession.from_queryset(data)

# @session_router.get("/session/{session_id}")
# async def get_specific_session(session_id:int):
#     data = await Session.filter(session_id=session_id).exists()
#     if not data:
#         raise HTTPException(status.HTTP_404_NOT_FOUND, detail="session Not Found")
#     return await GetSession.from_queryset(data)

@session_router.post("/session")
async def post_session(session: PostSession):
    data = await Session.create(**session.model_dump())
    return await GetSession.from_tortoise_orm(data)


@session_router.put("/session/{session_id}")
async def update_session(session_id: int, body: PutSession):
    exists = await Session.filter(session_id=session_id).exists()

    if not exists:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Session Not Found")

    # Update the session's fields (like 'active' or 'board')
    session_data = body.model_dump(exclude={"players"})

    await Session.filter(session_id=session_id).update(**session_data)

    if body.players:
        if len(body.players) >= 2:
            raise ValueError("The session alreayd full with 2 players")

        session_instance = await Session.get(session_id=session_id)
        # It will only allow two players, since I've set up in the schemas, but I'll add extra condition to make sure
        for player_data in body.players:
            # Check if a player with this ID already exists
            player_exists = await Player.filter(player_id=player_data.player_id).exists()

            if not player_exists:
                raise HTTPException(
                    status.HTTP_404_NOT_FOUND, 
                    detail=f"Player with ID {player_data.player_id} not found."
                )
            
            # If the player exists, update their details
            player_instance = await Player.get(player_id=player_data.player_id)
            player_instance.session = session_instance
            await player_instance.update_from_dict(player_data.model_dump(exclude_unset=True)).save()

    # Fetch and return the updated session with all its relationships loaded
    updated_session = await GetSession.from_queryset_single(Session.get(session_id=session_id).prefetch_related('players'))
    return updated_session

@session_router.delete("/session/{session_id}")
async def delete_todo(session_id: int):
    exists = await Session.filter(session_id=session_id).exists()

    if not exists:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Session Not Found")
    await Session.filter(session_id=session_id).delete()

    return f"The session {session_id} has be successfully deleted"
