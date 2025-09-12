import argparse
import asyncio
from fastapi import FastAPI
from tortoise import Tortoise
from api.routes.session import make_move, post_session, session_router, update_session 
from tortoise.contrib.fastapi import register_tortoise
from api.routes.player import player_router, post_player
from api.models.session import Session 
from api.models.player import Player
from api.schemas.player import PostPlayer
from api.schemas.session import Move, PostSession

app = FastAPI()
app.include_router(session_router)
app.include_router(player_router)

DATABASE_URL = "sqlite://game.db"
MODELS = {"models": ["api.models.session", "api.models.player"]}

register_tortoise(
    app=app,
    db_url=DATABASE_URL,
    add_exception_handlers=True,
    generate_schemas=True,
    modules=MODELS,
)

@app.get("/")
def index():
    return {"hello": "world"}


# ---- Script-mode helpers (no HTTP) ----
async def init_db_headless():
    """Initialize Tortoise without FastAPI for script mode."""
    await Tortoise.init(db_url=DATABASE_URL, modules=MODELS)
    await Tortoise.generate_schemas()

async def close_db_headless():
    await Tortoise.close_connections()


# In this example, I'll create session id from 1-10, player_id from 20-30 for better reading
# Play 4 games with 8 players, so we sure can have top 3 players in the end
async def create_session_players():

    await init_db_headless()

    # Create Session 1
    session1 = PostSession(session_id=1, board=[[0]*3 for _ in range(3)], active=True)
    await post_session(session1)
    p1 = PostPlayer(player_id=20, name="Alice", score=0, steps=0, session_id=session1.session_id)
    p2 = PostPlayer(player_id=21, name="Bob", score=0, steps=0, session_id=session1.session_id)
    await post_player(p1)
    await post_player(p2)
    # For update players to session, should use update_session
    await update_session(session1.session_id)
    
    # # Create Session 2
    session2 = PostSession(session_id=2, board=[[0]*3 for _ in range(3)], active=True)
    await post_session(session2)

    p3 = PostPlayer(player_id=22, name="Jack", score=0, steps=0, session_id=session2.session_id)
    p4 = PostPlayer(player_id=23, name="Lida", score=0, steps=0, session_id=session2.session_id)
    await post_player(p3)
    await post_player(p4)
    await update_session(session2.session_id)

    # Create Session 3
    session3 = PostSession(session_id=3, board=[[0]*3 for _ in range(3)], active=True)
    await post_session(session3)
    p5 = PostPlayer(player_id=24, name="Lily", score=0, steps=0, session_id=session3.session_id)
    p6 = PostPlayer(player_id=25, name="Karen", score=0, steps=0, session_id=session3.session_id)
    await post_player(p5)
    await post_player(p6)
    await update_session(session3.session_id)

    # Create Session 4
    session4 = PostSession(session_id=4, board=[[0]*3 for _ in range(3)], active=True)
    await post_session(session4)
    p7 = PostPlayer(player_id=26, name="Kate", score=0, steps=0, session_id=session4.session_id)
    p8 = PostPlayer(player_id=27, name="Susan", score=0, steps=0, session_id=session4.session_id)
    await post_player(p7)
    await post_player(p8)
    await update_session(session4.session_id)
    print(f"4 sessions and 8 players have been created, also assign players to the each session")
    await close_db_headless()


async def start_game1():
    await init_db_headless()
    print("------------------------------------------------Session 1 Started--------------------------------------------------")
    session = await Session.get(session_id=1)
    p1 = await Player.get(player_id=20)
    p2 = await Player.get(player_id=21)

    # Moves -> outcome: player_id = 20, Alice won
    move1 = Move(player_id=p1.player_id, row=1, col=1)
    print(f"Move 1 for {session.session_id}, and outcome is, {await make_move(session.session_id, move1)}")
    move2 = Move(player_id=p2.player_id, row=0, col=0)
    print(f"Move 2 for {session.session_id}, and outcome is {await make_move(session.session_id, move2)}")
    move3 = Move(player_id=p1.player_id, row=0, col=1)
    print(f"Move 3 for {session.session_id}, and outcome is, {await make_move(session.session_id, move3)}")
    move4 = Move(player_id=p2.player_id, row=1, col=0)
    print(f"Move 4 for {session.session_id}, and outcome is, {await make_move(session.session_id, move4)}")
    move5 = Move(player_id=p1.player_id, row=2, col=1)
    print(f"Move 5 for {session.session_id}, and outcome is {await make_move(session.session_id, move5)}")

    print("------------------------------------------------Session 1 Ended--------------------------------------------------")
    await close_db_headless()
    

async def start_game2():
    await init_db_headless()
    print("------------------------------------------------Session 2 Started--------------------------------------------------")

    session = await Session.get(session_id=2)
    p1 = await Player.get(player_id=22)
    p2 = await Player.get(player_id=23)

    # Moves -> outcome, the player_id = 22 is winning
    move1 = Move(player_id=p1.player_id, row=0, col=0)
    print(f"Move 1 for {session.session_id}, and outcome is, {await make_move(session.session_id, move1)}")
    move2 = Move(player_id=p2.player_id, row=0, col=1)
    print(f"Move 2 for {session.session_id}, and outcome is {await make_move(session.session_id, move2)}")
    move3 = Move(player_id=p1.player_id, row=1, col=0)
    print(f"Move 3 for {session.session_id}, and outcome is, {await make_move(session.session_id, move3)}")
    move4 = Move(player_id=p2.player_id, row=1, col=1)
    print(f"Move 4 for {session.session_id}, and outcome is, {await make_move(session.session_id, move4)}")
    move5 = Move(player_id=p1.player_id, row=2, col=0) 
    print(f"Move 5 for {session.session_id}, and outcome is {await make_move(session.session_id, move5)}")
    move6 = Move(player_id=p2.player_id, row=2, col=2)
    print(f"Move 6 for {session.session_id}, and outcome is {await make_move(session.session_id, move6)}")
    
    print("------------------------------------------------Session 2 Started--------------------------------------------------")
    await close_db_headless()

async def start_game3():
    await init_db_headless()

    print("------------------------------------------------Session 3 Started--------------------------------------------------")

    session = await Session.get(session_id=3)
    p1 = await Player.get(player_id=24)
    p2 = await Player.get(player_id=25)

    # Moves -> outcome is draw
    move1 = Move(player_id=p1.player_id, row=0, col=0)
    print(f"Move 1 for {session.session_id}, and outcome is, {await make_move(session.session_id, move1)}")

    move2 = Move(player_id=p2.player_id, row=0, col=1)
    print(f"Move 2 for {session.session_id}, and outcome is {await make_move(session.session_id, move2)}")
    
    move3 = Move(player_id=p1.player_id, row=0, col=2)
    print(f"Move 3 for {session.session_id}, and outcome is, {await make_move(session.session_id, move3)}")
    
    move4 = Move(player_id=p2.player_id, row=1, col=1)
    print(f"Move 4 for {session.session_id}, and outcome is, {await make_move(session.session_id, move4)}")
    
    move5 = Move(player_id=p1.player_id, row=1, col=0)
    print(f"Move 5 for {session.session_id}, and outcome is {await make_move(session.session_id, move5)}")

    move6 = Move(player_id=p2.player_id, row=1, col=2)
    print(f"Move 6 for {session.session_id}, and outcome is {await make_move(session.session_id, move6)}")
    
    move7 = Move(player_id=p1.player_id, row=2, col=1)
    print(f"Move 7 for {session.session_id}, and outcome is {await make_move(session.session_id, move7)}")
    
    move8 = Move(player_id=p2.player_id, row=2, col=0)
    print(f"Move 8 for {session.session_id}, and outcome is {await make_move(session.session_id, move8)}")
    
    move9 = Move(player_id=p1.player_id, row=2, col=2)
    print(f"Move 9 for {session.session_id}, and outcome is {await make_move(session.session_id, move9)}")
    
    print("------------------------------------------------Session 3 Ended--------------------------------------------------")
    await close_db_headless()

async def start_game4():
    await init_db_headless()

    print("------------------------------------------------Session 4 Started--------------------------------------------------")

    session = await Session.get(session_id=4)
    p1 = await Player.get(player_id=26)
    p2 = await Player.get(player_id=27)

    # Moves-> player_id 26, Kate is the winning 
    move1 = Move(player_id=p1.player_id, row=0, col=0)
    print(f"Move 1 for {session.session_id}, and outcome is, {await make_move(session.session_id, move1)}")
    move2 = Move(player_id=p2.player_id, row=1, col=0)
    print(f"Move 2 for {session.session_id}, and outcome is {await make_move(session.session_id, move2)}")
    move3 = Move(player_id=p1.player_id, row=0, col=1)
    print(f"Move 3 for {session.session_id}, and outcome is, {await make_move(session.session_id, move3)}")
    move4 = Move(player_id=p2.player_id, row=2, col=1)
    print(f"Move 4 for {session.session_id}, and outcome is, {await make_move(session.session_id, move4)}")
    move5 = Move(player_id=p1.player_id, row=0, col=2)
    print(f"Move 5 for {session.session_id}, and outcome is {await make_move(session.session_id, move5)}")

    print("------------------------------------------------Session 4 End--------------------------------------------------")
    await close_db_headless()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run script serve API.")
    parser.add_argument("--create", action="store_true", help="Start creating sessions and players")
    parser.add_argument("--script", action="store_true", help="start and simulate a game, judge and print result.")
    args = parser.parse_args()
    
    if args.create: # python3 main.py --create
        asyncio.run(create_session_players())
    elif args.script: # python3 main.py --script
        asyncio.run(start_game1())
        asyncio.run(start_game2())
        asyncio.run(start_game3())
        asyncio.run(start_game4())