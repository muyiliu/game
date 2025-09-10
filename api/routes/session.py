from fastapi import APIRouter, HTTPException,status
from api.models.session import Session
from api.schemas.session import GetSession, PostSession, PutSession

session_router = APIRouter(prefix="/api", tags=["session"])

# For the following are routers for session
@session_router.get("/session")
async def all_session():
    data = Session.all()
    return await GetSession.from_queryset(data)


@session_router.post("/session")
async def post_session(session: PostSession):
    row = await Session.create(**session.model_dump())
    
    return await GetSession.from_tortoise_orm(row)


@session_router.put("/session/{session_id}")
async def update_session(session_id: int, body: PutSession):
    data = body.model_dump()
    
    exists = await Session.filter(session_id=session_id).exists()

    if not exists:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Session Not Found")

    await Session.filter(session_id=session_id).update(**data)
    session = await GetSession.from_queryset_single(Session.get(session_id=session_id))
    
    return session


@session_router.delete("/session/{session_id}")
async def delete_todo(session_id: int):
    exists = await Session.filter(session_id=session_id).exists()

    if not exists:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Session Not Found")
    await Session.filter(session_id=session_id).delete()

    return f"The session {session_id} has be successfully deleted"
