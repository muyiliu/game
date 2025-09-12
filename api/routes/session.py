import heapq
from typing import Optional
from fastapi import APIRouter, HTTPException,status
from api.models.player import Player
from api.models.session import Session
from api.schemas.session import GetSession, Move, PostSession, PutSession, Move

session_router = APIRouter(prefix="/api", tags=["session"])

@session_router.get("/session")
async def all_session():
    data = Session.all()
    return await GetSession.from_queryset(data)


@session_router.post("/session")
async def post_session(session: PostSession):
    exists = await Session.filter(session_id=session.session_id).exists()
    if exists:
        raise ValueError(f" {session.session_id} already exist")
    data = await Session.create(**session.model_dump())
    return await GetSession.from_tortoise_orm(data)
    

@session_router.put("/session/{session_id}")
async def update_session(session_id: int, body:Optional[PutSession] = None):

    exists = await Session.filter(session_id=session_id).exists()

    if not exists:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Session Not Found")

    players = await Player.filter(session__session_id=session_id).values("player_id", "name")
    if len(players) > 2:
        raise ValueError("The session alreayd full with 2 players")
    
    if body:
        if body.players: # TODO: If players are changed, I need to update
            session_instance = await Session.get(session_id=session_id)
            # It will only allow two players, since I've set up in the schemas, but I'll add extra condition to make sure
            for player_data in body.players:
                # Check if a player with this ID already exists
                # player_exists = await Player.filter(player_id=player_data.player_id).exists()

                if not player_data:
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
    
    
@session_router.put("/session/{session_id}/move")
async def make_move(session_id: int, body: Move):
    session = await Session.get_or_none(session_id=session_id)
    if session:
        players = await Player.filter(session__session_id=session_id).values("player_id", "name")
        if len(players) > 2:
            raise ValueError("There are more than two players, you can't player the game")
    if not session:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="The session NOT been found")
    
    # TODO: if session active=False, you have to update the session, let it to be active, but you can't directly update here
    board = session.board

    if board[body.row][body.col] == 0:
        board[body.row][body.col] = body.player_id
        
    else:
        raise ValueError("The position has been taken")

    # player will make a move, so add 1 step at beignning 
    player = await Player.get(player_id=body.player_id)
    player.steps += 1
    await player.update_from_dict({"steps": player.steps}).save()

    winner = check_winner(board)
    if winner:
        player.score += 1
        await player.update_from_dict({"score":player.score}).save()
        top_three_players_score = await top_three_player_score()
        top_three_players_freq = await top_three_player_freq()
        return {"winner ": player.name, 
                "board ": board, 
                "Top 3 players based on score ": top_three_players_score,
                "Top 3 players based on freq": top_three_players_freq
                }
    else:
        draw = is_draw(board)
    
    if draw:
        session_id = session.session_id
        await session.update_from_dict({"board": board, "session_id": False}).save()
        top_three_players_score = await top_three_player_score()
        top_three_players_freq = await top_three_player_freq()
        return {"The session has been drawn" : {board}, 
                session_id : " has been inactived",
                "Top 3 players based on score ": top_three_players_score,
                "Top 3 players based on freq": top_three_players_freq
                }
    
    await session.update_from_dict({"board": board}).save()
    return {"The game is on going " : board}


def is_draw(board):
    for r in range(len(board)):
        for c in range(len(board[0])):
            if board[r][c] == 0:
                return False
    return True 


def check_winner(board):
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] and board[i][0] != 0: return board[i][0]
        if board[0][i] == board[1][i] == board[2][i] and board[0][i] != 0: return board[0][i]

    if board[0][0] == board[1][1] == board[2][2] and board[0][0] != 0: return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] != 0: return board[0][2]
    
    return None

# the score is larger the better, so I use max heap to find top 3 players
async def top_three_player_score():
    players = await Player.all().values("player_id", "name", "score")
    heap = []
    result = []

    for player in players:
        if player["score"] != 0:
            heapq.heappush(heap, (-player["score"], player["player_id"], player["name"]))

    if len(heap) < 3:
        return result 
    
    for _ in range(3):
        score, player_id, name = heapq.heappop(heap)
        result.append([name, -score]) # score, player_id
    
    return result

# base on the description, the lower the better, so I use min heap to find the top 3 players
async def top_three_player_freq(): 
    players = await Player.all().values("player_id", "name", "score", "steps")
    heap = []

    result = []
    for player in players:
        if player["score"] != 0:
            heapq.heappush(heap, ((player["score"]/player["steps"]), player["player_id"], player["name"]))
    
    if len(heap) < 3:
        return result
    
    for _ in range(3):
        freq, player_id, name = heapq.heappop(heap)
        result.append([name, round(freq, 2)]) # freq, player_id
        
    return result
    

@session_router.delete("/session/{session_id}")
async def delete_session(session_id: int):
    exists = await Session.filter(session_id=session_id).exists()

    if not exists:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Session Not Found")
    await Session.filter(session_id=session_id).delete()
    return f"The session {session_id} has been successfully deleted"
