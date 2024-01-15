from enum import Enum

class PowerupType(Enum):
    NO_OBSTACLE = 1
    LIFE = 2
    X2 = 3

class Powerup():
    def __init__(self, type, p=0.1, max_powerups=2, obstacle_runs=5) -> None:
        '''
        Inputs:
        - type: one of PowerupType class
        - p: probability of powerup showing up in certain run
        - max_powerups: max amount of this powerup that can show up in a single run
        - obstacle_runs: number of runs whether there will be no obstacles
        '''
        self.type = type
        self.p = p
        self.max_powerup = max_powerups
        if type == PowerupType.NO_OBSTACLE:
            self.obstacle_runs = obstacle_runs

    def powerup_activate(self, game):
        '''
        Activates powerup with probability self.p and places it randomly in the game

        Inputs:
        - game: from game.py, so we can get game.w and game.h to place the powerup randomly
        '''
        pass
    def powerup_playstep(self, game, ):
        '''
        Handles the neccesary adjustments in the game when a powerup is acquired

        Inputs: 
        - game: Make adjustments to game.lives, game.score_multiplier, or game.obstacle_powerup
        '''
        
        if self.type == PowerupType.NO_OBSTACLE:
            game.obstacle_powerup = self.obstacle_runs
        elif self.type == PowerupType.LIFE:
            game.lives += 1
        elif self.type == PowerupType.X2:
            game.score_multiplier += 1
