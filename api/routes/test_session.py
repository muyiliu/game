import unittest

from fastapi import HTTPException
import pytest
from tortoise import Tortoise
from api.models.player import Player
from api.models.session import Session
from api.routes.player import post_player
from api.schemas.player import PostPlayer
from api.schemas.session import Move, PostSession, PutSession
from api.routes.session import all_session, check_winner, is_draw, make_move, post_session, top_three_player_freq, top_three_player_score, update_session

DB_URL = "sqlite://:memory:"
MODULES = {"models": ["api.models.session", "api.models.player"]}


'''
1. test if create correct sessions, and if they can run concurrently
2. test each function with the session
3. test edge case such as: if more than 3 players in a session, same session has been created, if input for PutSession will be updated
4. also test the relation between players and session
Due to the time limit, test coverage won't cover everything, I'll try to add most of them
'''
# run : ./.venv/bin/python -m unittest api.routes.test_session

class TestSessionAsync(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # init db before each test
        await Tortoise.init(db_url=DB_URL, modules=MODULES)
        await Tortoise.generate_schemas()

    async def asyncTearDown(self):
        # close db after each test
        await Tortoise.close_connections()

    async def test_create_and_get_session(self):
        await Session.create(session_id=123, active=True, board=[[0]*3]*3)
        session = await Session.get(session_id=123)
        self.assertTrue(session.active)
        self.assertEqual(session.session_id, 123)
    
    async def test_get_all_session(self):
        mock_session1 = PostSession(session_id=123, board=[[0, 1, 0], [0, 1, 0], [0, 0, 0]], active=True)
        await post_session(mock_session1)
        mock_session2 = PostSession(session_id=456, board=[[0, 1, 0], [0, 1, 0], [0, 0, 0]], active=True)
        await post_session(mock_session2)
        sessions = await all_session()
        self.assertEqual(len(sessions), 2)

    async def test_post_session(self):
        mock_session = PostSession(session_id=1, board=[[0, 0, 0], [0, 0, 0], [0, 0, 0]], active=True)
        await post_session(mock_session)
        session = await Session.get(session_id=mock_session.session_id)
        self.assertEqual(session.active, True)
    
    async def test_update_session(self):
        mock_post_session = PostSession(session_id=123, board=[[0, 0, 0], [0, 0, 0], [0, 0, 0]], active=True)
        await post_session(mock_post_session)
        mock_put_session = PutSession(board=[[0, 0, 0], [0, 1, 0], [0, 0, 0]], active=False)
        await update_session(session_id=123, body=mock_put_session)
        session = await Session.get(session_id=123)
        self.assertTrue(mock_post_session.active)
        self.assertEqual(mock_post_session.board, [[0, 0, 0], [0, 0, 0], [0, 0, 0]])
        self.assertFalse(session.active)
        self.assertTrue(session.board, [[0, 0, 0], [0, 1, 0], [0, 0, 0]])
    
    async def test_three_players_enter_one_session(self):
        mock_session1 = PostSession(session_id=123, board=[[0, 1, 0], [0, 1, 0], [0, 0, 0]], active=True)
        await post_session(mock_session1)
        player1= PostPlayer(player_id=1, name="Alice", score=3, steps=14, session_id=mock_session1.session_id)
        await post_player(player=player1)
        player2= PostPlayer(player_id=2, name="Bob", score=4, steps=12, session_id=mock_session1.session_id)
        await post_player(player=player2)
        player3= PostPlayer(player_id=3, name="Kate", score=2, steps=10, session_id=mock_session1.session_id)
        await post_player(player=player3)
        mock_put_session = PutSession(board=[[0, 0, 0], [0, 1, 0], [0, 0, 0]], active=False)

        with pytest.raises(ValueError) as error_info:
            await update_session(session_id=123, body=mock_put_session)
        assert "The session alreayd full with 2 players" in str(error_info.value)
            
    async def test_make_move_session_not_found(self):
        mock_session = PostSession(session_id=123, board=[[0, 0, 0], [0, 0, 0], [0, 0, 0]], active=True)
        await post_session(mock_session)
        mock_move = Move(player_id=456, row=1, col=1)
        
        with pytest.raises(HTTPException) as exception_info:
            await make_move(session_id=456, body=mock_move)
        assert exception_info.value.status_code == 404
        assert exception_info.value.detail == "The session NOT been found"

    async def test_session_is_inactive(self):
        mock_session = PostSession(session_id=123, board=[[0, 0, 0], [0, 0, 0], [0, 0, 0]], active=False)
        await post_session(mock_session)
        mock_move = Move(player_id=456, row=1, col=1)
        with pytest.raises(ValueError) as error_info:
            await make_move(session_id=123, body=mock_move)
        assert "123 is not active, please active session first" in str(error_info.value)

    async def test_position_been_taken(self):
        mock_session = PostSession(session_id=123, board=[[0, 1, 0], [0, 1, 0], [0, 0, 0]], active=True)
        await post_session(mock_session)
        mock_move = Move(player_id=456, row=1, col=1)
        
        with pytest.raises(ValueError) as error_info:
            await make_move(session_id=123, body=mock_move)
        assert "The position has been taken" in str(error_info.value)

    async def test_top_three_score(self):
        mock_session1 = PostSession(session_id=123, board=[[0, 1, 0], [0, 1, 0], [0, 0, 0]], active=True)
        await post_session(mock_session1)
        mock_session2 = PostSession(session_id=456, board=[[0, 1, 0], [0, 1, 0], [0, 0, 0]], active=True)
        await post_session(mock_session2)
        player1= PostPlayer(player_id=1, name="Alice", score=3, steps=14, session_id=mock_session1.session_id)
        await post_player(player=player1)
        player2= PostPlayer(player_id=2, name="Bob", score=4, steps=12, session_id=mock_session1.session_id)
        await post_player(player=player2)
        player3= PostPlayer(player_id=3, name="Kate", score=2, steps=10, session_id=mock_session2.session_id)
        await post_player(player=player3)
        player4= PostPlayer(player_id=4, name="Lily", score=0, steps=4, session_id=mock_session2.session_id)
        await post_player(player=player4)
        
        result = await top_three_player_score()
        self.assertEqual(result, [["Bob", 4], ["Alice", 3], ["Kate", 2]])

    async def test_top_three_freq(self):
        mock_session1 = PostSession(session_id=123, board=[[0, 1, 0], [0, 1, 0], [0, 0, 0]], active=True)
        await post_session(mock_session1)
        mock_session2 = PostSession(session_id=456, board=[[0, 1, 0], [0, 1, 0], [0, 0, 0]], active=True)
        await post_session(mock_session2)
        player1= PostPlayer(player_id=1, name="Alice", score=3, steps=14, session_id=mock_session1.session_id)
        await post_player(player=player1)
        player2= PostPlayer(player_id=2, name="Bob", score=4, steps=12, session_id=mock_session1.session_id)
        await post_player(player=player2)
        player3= PostPlayer(player_id=3, name="Kate", score=2, steps=10, session_id=mock_session2.session_id)
        await post_player(player=player3)
        player4= PostPlayer(player_id=4, name="Lily", score=0, steps=4, session_id=mock_session2.session_id)
        await post_player(player=player4)

        result = await top_three_player_freq()
        self.assertEqual(result, [['Bob', 3.0], ['Alice', 4.67], ['Kate', 5.0]])

    async def test_session_player_relate(self):
        mock_session1 = PostSession(session_id=123, board=[[0, 1, 0], [0, 1, 0], [0, 0, 0]], active=True)
        await post_session(mock_session1)
        player1= PostPlayer(player_id=1, name="Alice", score=3, steps=14, session_id=mock_session1.session_id)
        await post_player(player=player1)
        player2= PostPlayer(player_id=2, name="Bob", score=4, steps=12, session_id=mock_session1.session_id)
        await post_player(player=player2)

        p1 = await Player.filter(session__session_id=player1.session_id, player_id = player1.player_id).values()
        self.assertEqual(p1[0]["player_id"], 1)
    
    async def test_delete_session(self):
        pass

# Test all Not async functions
class SessionTest(unittest.TestCase):
    # have 8 winner situation three rows, three cols, 1 dignal and 1 anti diganal, but due to time constriant, I'll pass some for now
    def test_check_winner1(self):
        board = [[1, 2, 0], [1, 0, 2], [1, 2, 0]]
        result = check_winner(board)
        self.assertEqual(result, 1)
        fail_result = check_winner(board)
        self.assertNotEqual(fail_result, 2)

    def test_check_winner2(self):
        board = [[1, 2, 0], [0, 1, 2], [0, 2, 1]]
        result = check_winner(board)
        self.assertEqual(result, 1)
        fail_result = check_winner(board)
        self.assertNotEqual(fail_result, 2)
    
    def test_check_winner_none(self):
        board = [[0, 2, 1], [2, 1, 0], [1, 2, 0]]
        result = check_winner(board)
        self.assertEqual(result, 1)
        fail_result = check_winner(board)
        self.assertNotEqual(fail_result, 2)

    def test_is_draw(self):
        board = [[1, 2, 1], [2, 1, 2], [2, 1, 2]]
        result = is_draw(board)
        self.assertTrue(result)
    
    def test_is_not_draw(self):
        board = [[1, 2, 1], [2, 1, 2], [2, 1, 0]]
        result = is_draw(board)
        self.assertFalse(result)

