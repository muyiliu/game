from fastapi import FastAPI
from api.routes.session import session_router 
from tortoise.contrib.fastapi import register_tortoise
from api.routes.player import player_router
# import uvicorn 

app = FastAPI()
app.include_router(session_router)
app.include_router(player_router)
register_tortoise(
    app=app,
    db_url="sqlite://game.db",
    add_exception_handlers=True,
    generate_schemas=True,
    modules={"models": ["api.models.session", "api.models.player", "api.models"]}
)

@app.get("/")

def index():
    return {"hello": "world"}

if __name__ == "__main__":
    print("passed")
#     uvicorn.run("main:app", reload=True) # uvicorn main:app --reload
# http://127.0.0.1:8000/api/session -> []
# http://127.0.0.1:8000/api/player -> {player: in progress}