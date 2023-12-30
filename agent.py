import torch
import random
import numpy as np
from game import SnakeGameAI, Direction, Point
from collections import deque

MAX_MEMORY = 100000
BATCH_SIZE = 1000
LEARNING_RATE = 0.001

class Agent:
    def __init__(self) -> None:
        self.num_games = 0
        self.epsilon = 0 # for randomness
        self.gamma = 0 # discount rate
        self.memory = deque(maxlen=MAX_MEMORY) # popleft() if it reaches the max memory
        # TODO: model, trainer


    def get_state(self, game: SnakeGameAI):
        head = game.snake
        left_pt = Point(head.x - 20, head.y)
        right_pt = Point(head.x + 20, head.y)
        up_pt = Point(head.x, head.y - 20)
        down_pt = Point(head.x, head.y + 20)

        left = game.direction == Direction.LEFT
        right = game.direction == Direction.RIGHT
        up = game.direction == Direction.UP
        down = game.direction == Direction.DOWN

        # TODO: write the state to be returned


    def remember(self, state, action, reward, next_state, game_over):
        pass

    def train_long_memory(self):
        pass

    def train_short_memory(self, state, action, reward, next_state, game_over):
        pass

    def get_action(self, state):
        pass


def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = SnakeGameAI()
    while True:
        # get old state
        old_state = agent.get_state(game) 

        # get the next action based on the model
        next_action = agent.get_action(old_state) 

        # apply move to game and get the new state
        reward, done, score = game.play_step(next_action)
        new_state = agent.get_state(game)

        # train short memory
        agent.train_short_memory(old_state, next_action, reward, new_state, done)

        # remember
        agent.remember(old_state, next_action, reward, new_state, done)

        if done:
            # train long memory
            game.reset()
            agent.num_games += 1
            agent.train_long_memory()
            if score > record:
                record = score
                # agent.model.save()
            print('Game:', agent.num_games, ', Score:', score, ', Record:', record)

            # TODO: plot



if __name__ == '__main__':
    train()