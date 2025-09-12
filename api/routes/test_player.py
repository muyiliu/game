import unittest

from fastapi import HTTPException
import pytest
from tortoise import Tortoise
from api.models.player import Player
from api.models.session import Session
from api.routes.player import post_player, update_player
from api.routes.session import post_session
from api.schemas.player import PostPlayer, PutPlayer
from api.schemas.session import PostSession, PutSession

DB_URL = "sqlite://:memory:"
MODULES = {"models": ["api.models.session", "api.models.player"]}

# run : ./.venv/bin/python -m unittest api.routes.test_player
class TestPlayerAsync(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        await Tortoise.init(db_url=DB_URL, modules=MODULES)
        await Tortoise.generate_schemas()

    async def asyncTearDown(self):
        await Tortoise.close_connections()

    async def test_create_and_get_player(self):
        mock_session1 = PostSession(session_id=123, board=[[0, 1, 0], [0, 1, 0], [0, 0, 0]], active=True)
        await post_session(mock_session1)
        await Player.create(player_id=1, name="Alice", score=3, steps=12, session_id=mock_session1.session_id)
        player = await Player.get(player_id=1)
        self.assertEqual(player.player_id, 1)
        self.assertEqual(player.name, "Alice")

    async def test_get_all_player(self):
        mock_session1 = PostSession(session_id=123, board=[[0, 1, 0], [0, 1, 0], [0, 0, 0]], active=True)
        await post_session(mock_session1)
        player1= PostPlayer(player_id=1, name="Alice", score=3, steps=14, session_id=mock_session1.session_id)
        await post_player(player=player1)
        player2= PostPlayer(player_id=2, name="Bob", score=4, steps=12, session_id=mock_session1.session_id)
        await post_player(player=player2)

        players = await Player.all()
        self.assertEqual(len(players), 2)
    
    async def test_post_player(self):
        mock_session1 = PostSession(session_id=123, board=[[0, 1, 0], [0, 1, 0], [0, 0, 0]], active=True)
        await post_session(mock_session1)
        player1= PostPlayer(player_id=1, name="Alice", score=3, steps=14, session_id=mock_session1.session_id)
        await post_player(player=player1)
        player = await Player.get(player_id=player1.player_id)
        self.assertEqual(player.name, "Alice")

    async def test_update_player(self):
        mock_session1 = PostSession(session_id=123, board=[[0, 0, 0], [0, 0, 0], [0, 0, 0]], active=True)
        await post_session(mock_session1)
        player1= PostPlayer(player_id=1, name="Alice", score=3, steps=14, session_id=mock_session1.session_id)
        await post_player(player=player1)
        
        mock_put_player = PutPlayer(name="Alice", score=6, steps=14, session_id=mock_session1.session_id)
        await update_player(player_id=1, body=mock_put_player)
        player = await Player.get(player_id=1)
        self.assertEqual(player.score, 6)

    async def test_delete_player(self):
        mock_session1 = PostSession(session_id=123, board=[[0, 0, 0], [0, 0, 0], [0, 0, 0]], active=True)
        await post_session(mock_session1)
        player1= PostPlayer(player_id=1, name="Alice", score=3, steps=14, session_id=mock_session1.session_id)
        await post_player(player=player1)

    async def test_player_not_exist(self):
        mock_session1 = PostSession(session_id=123, board=[[0, 0, 0], [0, 0, 0], [0, 0, 0]], active=True)
        await post_session(mock_session1)
        player1= PutPlayer(name="Alice", score=3, steps=14, session_id=mock_session1.session_id)
        
        with pytest.raises(HTTPException) as exception_info:
            await update_player(player_id=2, body=player1)
        assert exception_info.value.status_code == 404
        assert exception_info.value.detail == "Player Not Found"        

    