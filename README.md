# Game


TLDR
Steps to start script:
1. delete game.db, game.db-shm, and game.db-wal to start from fresh (current project is for completion)
2. run python3 main.py --create
3. run python3 main.py --script

You should see the results of 4 session games, including top 3 players based on score and freq.

# Flow

## Thought Process
At first, I was thinking directly let Player be included under Session, after the implementation, I don't think it has great extensibility because the generally game flow will be players create their own characters and names, and enter the session they want. If I directly created players under the Session data model, it wouldn't feasible. This cost me some time to think and straight out my mind.   
