# Game


TLDR
Steps to start script:
1. delete game.db, game.db-shm, and game.db-wal to start from fresh (current project is for completion)
2. run `uvicorn main:app --reload` (this generate the database)
3. run **python3 main.py --create**
4. run **python3 main.py --script**

You should see the results of 4 mock session games, including top 3 players based on score and freq.


Moreover, if you would like to fetch through localhost, can you do:
1. run **uvicorn main:app --reload**
2. run your localhost (http://127.0.0.1:8000/) on postman or browser
# # uvicorn main:app --reload
# # http://127.0.0.1:8000/api/session -> []
# # http://127.0.0.1:8000/api/player -> []

## Flow

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
- top 3 players will only show when there is draw or winner 
data model discussion


## Data Model
## Thought Process
At first, I was thinking directly let Player be included under Session, after the implementation, I don't think it has great extensibility because the generally game flow will be players create their own characters and names, and enter the session they want. If I directly created players under the Session data model, it wouldn't feasible. This cost me some time to think and straight out my mind.   

## Testing
There are two tests, one for player and another for session, here are two different command:
**./.venv/bin/python -m unittest api.routes.test_session**

**./.venv/bin/python -m unittest api.routes.test_player**
<img width="620" height="73" alt="Screenshot 2025-09-12 at 1 28 00 PM" src="https://github.com/user-attachments/assets/29531f4e-8c96-4ea2-93aa-e5e7e0db9047" />

testing is really important, sometime I would forget to check some edge condition, through the testing I will easy to detect. Detected logic errors would be pretty striaghtforward  

## Result
