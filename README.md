# Game


## TLDR </br>
Steps to start script and see the mock games: <br>
1. delete `game.db`, `game.db-shm`, and `game.db-wal` to start from fresh
2. run `uvicorn main:app --reload` (this generate the database)
3. run `python3 main.py --create`
4. run `python3 main.py --script`
You should see the results of 4 mock session games, including top 3 players based on score and freq. (attached pic in the end)

For testing: 
run: 
`./.venv/bin/python -m unittest api.routes.test_session`
and
`./.venv/bin/python -m unittest api.routes.test_player`

Moreover, if you would like to fetch through localhost, can you do:
1. run `uvicorn main:app --reload`
2. run your localhost (http://127.0.0.1:8000/) on postman or browser

`http://127.0.0.1:8000/api/session` -> []
`http://127.0.0.1:8000/api/player` -> []

**All results attached in the end of READMe**

## Thought Process
At first, I was thinking directly let `Player` data model be included under `Session ` data model, after thinking about it, I don't think it has great extensibility because the generally game flow will be creating sessions, and players create their own characters and names, and enter the session they want at beginning. If I directly created players under the Session data model, it wouldn't feasible. This cost me some time to think. 
After clear about the flow of game, I was able to create `Session` and `Player`, when it came to player the game, I create `Move` model, so each step won't be impacting another `Session` because each `Session` has its own board. After finished each game, showing the score and frequency based on steps and score. Instead of deleted the session directly, I decided to mark the session as inactive, so next time when it came to the same that already exists in the Sessions, I can reactivate it. 
Due to the limit of time, I was able to implement all the features that I want, such as reactivate the session when it already existed in the database, fully check all edge cases and situation, and increase test coverage etc

## Flow

The flow of work of creating sessions and players should be:
1. Create sessions, we can have multiple session and players to play games at the same time 
2. create players and select the game/session, and it should use update function for sessions, if more than two players selected one session, the 
session will deny 3rd player to enter the game
3. once the game has start, players can place their id on the board
4. the one who won in the end, will incremenet 1 in the score, and in the meanwhile record their total steps for checking frequency  
5. the one lost, the score won't change, but will add the steps, so we can get frequency
6. If game is draw, record the steps only
7. in the end, get top 3 player with highest score, and another 3 based on frequency. If we don't have enough players, we should return empty list, or words
8. After the games are ended, we will mark the sessions as inactive, instead of deleting.
   
- top 3 players will only show when there is draw or winner 


## Data Model

Session:
  session_id: int
  board: board
  active: bool
  players: Player (ReverseRelation)

Player: 
  player_id: int
  name: str
  score: int
  steps: int
  session: Session (ForeignKeyRelation)

  

## Testing
There are two tests, one for player and another for session, here are two different command:
`./.venv/bin/python -m unittest api.routes.test_session`
`./.venv/bin/python -m unittest api.routes.test_player`

<img width="620" height="73" alt="Screenshot 2025-09-12 at 1 28 00 PM" src="https://github.com/user-attachments/assets/29531f4e-8c96-4ea2-93aa-e5e7e0db9047" />
<img width="526" height="71" alt="Screenshot 2025-09-12 at 1 27 38 PM" src="https://github.com/user-attachments/assets/ceb605bc-187e-4460-8b4d-81a75e5978da" />

Testing is really important, sometime there are some edge cases I didn't notice or pay attention, through writing the testing, it's easy to detect and fix. I tried to cover as much as testing I can.

## Result
<img width="1452" height="542" alt="Screenshot 2025-09-12 at 1 32 18 PM" src="https://github.com/user-attachments/assets/361d41b4-c403-448d-ab62-99fb3f50c2f8" />
