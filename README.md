# Game


TLDR
Steps to start script:
1. delete game.db, game.db-shm, and game.db-wal to start from fresh (current project is for completion)
2. run uvicorn main:app --reload (this generate the database)
3. run python3 main.py --create
4. run python3 main.py --script

You should see the results of 4 mock session games, including top 3 players based on score and freq.
Unit test: you can run ./.venv/bin/python -m unittest discover -s . -p "*_test.py for all test

Moreover, if you would like to fetch through localhost, can you do:
1. run uvicorn main:app --reload
2. run your localhost (http://127.0.0.1:8000/) on postman or browser


## Flow


## Data Model
## Thought Process
At first, I was thinking directly let Player be included under Session, after the implementation, I don't think it has great extensibility because the generally game flow will be players create their own characters and names, and enter the session they want. If I directly created players under the Session data model, it wouldn't feasible. This cost me some time to think and straight out my mind.   


## Result
