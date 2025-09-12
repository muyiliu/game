import unittest

from tortoise import Tortoise
from api.models.session import Session
from api.schemas.session import PostSession
from api.routes.session import check_winner, post_session

DB_URL = "sqlite://:memory:"
MODULES = {"models": ["api.models.session", "api.models.player"]}

class TestMyAsyncFunction(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # init db before each test
        await Tortoise.init(db_url=DB_URL, modules=MODULES)
        await Tortoise.generate_schemas()

    async def asyncTearDown(self):
        # close db after each test
        await Tortoise.close_connections()

    async def test_create_and_get_session(self):
        # arrange
        await Session.create(session_id=123, active=True, board=[[0]*3]*3)

        # act
        obj = await Session.get(session_id=123)

        # assert
        self.assertTrue(obj.active)
    

    async def test_my_async_function(self):
        mock_session = PostSession(session_id=1, board=[[0, 0, 0], [0, 0, 0], [0, 0, 0]], active=True)
        await post_session(mock_session)
        obj = await Session.get(session_id=mock_session.session_id)
        self.assertEqual(obj.active, True)
    
        

class SessionTest(unittest.TestCase):

    # successfully have 1 winner
    def test_check_winner(self):
        board = [[1, 2, 0], [1, 0, 2], [1, 2, 0]]
        result = check_winner(board)
        self.assertEqual(result, 1)

        fail_result = check_winner(board)
        self.assertNotEqual(fail_result, 2)


if __name__ == "__main__":
    unittest.main()





# python -m unittest test_session.py

# unittest
# python -m unittest api.routes.test_session
# ./.venv/bin/python -m unittest api.routes.test_session


# # or discover all tests
# python -m unittest discover -s . -p "*_test.py"
# ./.venv/bin/python -m unittest discover -s . -p "*_test.py