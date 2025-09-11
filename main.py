import argparse
import asyncio
from typing import List, Optional
from fastapi import FastAPI
from tortoise import Tortoise
from api.routes.session import make_move, post_session, session_router, update_session 
from tortoise.contrib.fastapi import register_tortoise
from api.routes.player import player_router, post_player
from api.models.session import Session 
from api.models.player import Player
from api.schemas.player import PostPlayer
from api.schemas.session import Move, PostSession, PutSession

app = FastAPI()
app.include_router(session_router)
app.include_router(player_router)
# register_tortoise(
#     app=app,
#     db_url="sqlite://game.db",
#     add_exception_handlers=True,
#     generate_schemas=True,
#     modules={"models": ["api.models.session", "api.models.player", "api.models"]}
# )

# @app.get("/")

# def index():
#     return {"hello": "world"}



# if __name__ == "__main__":
#     print("passed")
# #     uvicorn.run("main:app", reload=True) # uvicorn main:app --reload
# # http://127.0.0.1:8000/api/session -> []
# # http://127.0.0.1:8000/api/player -> {player: in progress}

DATABASE_URL = "sqlite://game.db"
MODELS = {"models": ["api.models.session", "api.models.player", "api.models"]}

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

'''
The flow of work of creating sessions and players should be:
1. when players enter the game, the game should create a session for them
2. players are able to enter the game by selecting session, if more than two players selected one session, the 
session will deny 3rd player to enter the game
3. once the game has start, players can player place their id on the board
4. the one who won in the end, will incremenet 1 in the score, and in the meanwhile record their total steps for winning
5. the one lost, the score won't change, but will add the steps, so we can get frequency
6. If game is draw, record the steps only
7. in the end, get top 3 player with highest score, and another 3 based on frequency.

- we can have multiple session and players to play games at the same time, if one of sessions has end,
delete the session
'''
# In this example, I'll create session id from 1-10, player_id from 20-30 for better reading
# Play 4 games with 8 players, so we sure can have top 3 players
async def create_session_players():

    await init_db_headless()

    # Create Session 1
    session1 = PostSession(session_id=1, board=[[0]*3 for _ in range(3)])
    await post_session(session1)

    p1 = PostPlayer(player_id=20, name="Alice", score=0, steps=0, session_id=session1.session_id)
    
    p2 = PostPlayer(player_id=21, name="Bob", score=0, steps=0, session_id=session1.session_id)
    p3 = PostPlayer(player_id=31, name="Jack", score=0, steps=0, session_id=session1.session_id)

    await post_player(p1)
    await post_player(p2)
    await post_player(p3)

    # For update players to session, should use PutSession
    ps = PutSession(board=[[0]*3 for _ in range(3)])
    await update_session(session1.session_id, ps)
    
    # # Create Session 2
    # session2 = PostSession(session_id=2, board=[[0]*3 for _ in range(3)])

    # # Create Player 2 and 3 
    # p3 = PostPlayer(player_id=22, name="Jack", score=0, steps=0)
    # p4 = PostPlayer(player_id=23, name="Lida", score=0, steps=0)
    # await post_player(p3)
    # await post_player(p4)
    # await post_session(session2)

    # session3 = PostSession(session_id=2, active=True, board=[[0]*3 for _ in range(3)])


    await close_db_headless()


# async def update_game(players:list[PostPlayer], session: PostSession):
async def start_game1():
    """
    Creates a session + two players, sets a board, judges the winner, prints, and exits.
    """
    await init_db_headless()


    # p1 = PostPlayer(player_id=10, name="Alice", playing=True, score=0)
    # p2 = PostPlayer(player_id=11, name="Bob", playing=True, score=0)
    session = await Session.get(session_id=1)
    p1 = await Player.get(player_id=20)
    p2 = await Player.get(player_id=21)
    players = await Player.all().values("player_id", "name", "score")
    print(f"Here are all players:{players}")

    # Moves
    move1 = Move(player_id=p1.player_id, row=1, col=1)
    r = await make_move(session.session_id, move1)

    move2 = Move(player_id=p2.player_id, row=0, col=0)
    await make_move(session.session_id, move2)
    
    move3 = Move(player_id=p1.player_id, row=0, col=1)

    await make_move(session.session_id, move3)

    move4 = Move(player_id=p2.player_id, row=1, col=0)
    await make_move(session.session_id, move4)

    move5 = Move(player_id=p1.player_id, row=2, col=1)
    winner = await make_move(session.session_id, move5)
    print("this is our winner", winner)
    print("here is r after movement",r)

    b = await Session.all().values("board")
    print("here is the board", b)
    player_score = await Player.all().values("score", "player_id", "name", "steps")
    print("here is the player_score", player_score)
    
    await close_db_headless()


# ---- Entry point ----
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run script seeding/judging and/or serve API.")
    parser.add_argument("--create", action="store_true", help="Start creating sessions and players")

    parser.add_argument("--script", action="store_true", help="start and simulate a game, judge and print result.")

    parser.add_argument("--serve", action="store_true", help="Serve the FastAPI app with uvicorn.")
    parser.add_argument("--host", default="127.0.0.1", help="Host for --serve (e.g., 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port for --serve")
    args = parser.parse_args()
    
    # if args.create:
    #      asyncio.run(create_session_players()) # python3 main.py --create
    if args.script: # python3 main.py --script 
        # asyncio.run(script_seed_and_judge())
            # players, session = asyncio.run(create_session())

            # asyncio.run(update_game(players, session))
        asyncio.run(start_game1())
    else:
        asyncio.run(create_session_players())

    # if args.serve:
    #     import uvicorn
    #     uvicorn.run("main:app", host=args.host, port=args.port, reload=True)
    # elif not args.script:
    #     # If no flags, do nothing special (avoid surprising behavior during automated imports)
    #     print("Tip: use --script to seed/judge, --serve to run the API, or both.")