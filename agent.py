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
        self.model = None
        self.trainer = None
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

        state = [
            # Danger Straight
            (left and game.is_collision(left_pt)) or
            (right and game.is_collision(right_pt)) or
            (up and game.is_collision(up_pt)) or
            (down and game.is_collision(down_pt)),

            # Danger Right
            (left and game.is_collision(up_pt)) or
            (right and game.is_collision(down_pt)) or
            (up and game.is_collision(right_pt)) or
            (down and game.is_collision(left_pt)),

            # Danger Left
            (left and game.is_collision(down_pt)) or
            (right and game.is_collision(up_pt)) or
            (up and game.is_collision(left_pt)) or
            (down and game.is_collision(right_pt)),

            # Direction
            left, 
            right,
            up,
            down,

            # Food location
            game.food.x < game.head.x, # Food Left
            game.food.x > game.head.x, # Food Right
            game.food.y < game.head.y, # Food Up
            game.food.y > game.head.y, # Food Down
        ]

        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, game_over):
        self.memory.append((state, action, reward, next_state, game_over))

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            sample = random.sample(self.memory, BATCH_SIZE) # returns list of tuples
        else:
            sample = self.memory
        states, actions, rewards, next_states, game_overs = zip(*sample)
        
        self.trainer.train_step(states, actions, rewards, next_states, game_overs)

    def train_short_memory(self, state, action, reward, next_state, game_over):
        self.trainer.train_step(state, action, reward, next_state, game_over)

    def get_action(self, state):
        # do random move or predicted move: tradeoff b/w exploration and exploitation in deep learning
        self.epsilon = 80 - self.num_games
        move = [0, 0, 0]
        if random.randint(0, 200) < self.epsilon:
            dir = random.randint(0, 2)
            move[dir] = 1
        else:
            tensor_state = torch.tensor(state, dtype=torch.float)
            prediction = self.model.predict(tensor_state)
            dir = torch.argmax(prediction).item()
            move[dir] = 1

        return move


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