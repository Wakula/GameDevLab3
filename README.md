# GameDevLab3

test
```
python run.py
```
Controls - WASD
    '''Connect''' # Send from CLIENT until receive 1: GameStarted
    '''GameStarted,''' # Send from SERVER until receive 2: GameStartedOK
    '''GameStartedOK,''' # Send from CLIENT until receive 3: GameState
    # Start game and start movement
    '''GameState,''' # Send from SERVER until ?
    '''PlayerState,''' # Send from CLIENT until ?
    # SHOOT
    '''ShootEvent,''' # Send from CLIENT/SERVER until receive 6: ShootOK
    '''ShootOK''' # Send from SERVER/CLIENT until receive package with greater id
    '''GetShot''' # Send from SERVER
    '''GetShotOK,''' # Send from CLIENT
