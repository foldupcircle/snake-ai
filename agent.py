import torch
import random
import numpy as np
from game import BLOCK_SIZE, SnakeGameAI, Direction, Point
from collections import deque
from model import Linear_QNet, QTrainer
from helper import plot

# Model Parameters
MAX_MEMORY = 100000
BATCH_SIZE = 1000
LEARNING_RATE = 0.001

class Agent:
    def __init__(self) -> None:
        self.num_games = 0
        self.epsilon = 0 # for randomness
        self.gamma = 0.9 # discount rate => can play around with this value (< 1)
        self.memory = deque(maxlen=MAX_MEMORY) # popleft() if it reaches the max memory
        self.model = Linear_QNet(14, 256, 3)
        self.trainer = QTrainer(self.model, LEARNING_RATE, self.gamma)

    def get_state(self, game: SnakeGameAI):
        '''
        Returns the appropriate state of the snake, which consists of 
        [
            Danger Straight, Danger Right, Danger Left, => is there obstacle, snake, or border next to snake head in that direction?
            left, right, up, down, => Direction snake is going
            food left, food right, food up, food down, => where food is in relation to the snake head
            obstacle straight, obstacle left, obstacle right => 'sensors' on how far obstacle is to straight, left, and right
        ]
        '''
        head = game.snake[0]
        left_pt = Point(head.x - BLOCK_SIZE, head.y)
        right_pt = Point(head.x + BLOCK_SIZE, head.y)
        up_pt = Point(head.x, head.y - BLOCK_SIZE)
        down_pt = Point(head.x, head.y + BLOCK_SIZE)

        left = game.direction == Direction.LEFT
        right = game.direction == Direction.RIGHT
        up = game.direction == Direction.UP
        down = game.direction == Direction.DOWN

        obstacle_straight, obstacle_left, obstacle_right = game.find_obstacles()

        if game.direction == Direction.LEFT or game.direction == Direction.RIGHT:
            obstacle_straight = round(obstacle_straight * BLOCK_SIZE / game.w, 3)
            obstacle_left = round(obstacle_left * BLOCK_SIZE / game.h, 3)
            obstacle_right = round(obstacle_right * BLOCK_SIZE / game.h, 3)
        elif game.direction == Direction.UP or game.direction == Direction.DOWN:
            obstacle_straight = round(obstacle_straight * BLOCK_SIZE / game.h, 3)
            obstacle_left = round(obstacle_left * BLOCK_SIZE / game.w, 3)
            obstacle_right = round(obstacle_right * BLOCK_SIZE / game.w, 3)

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

            # Space till obstacle
            obstacle_straight,
            obstacle_left,
            obstacle_right
        ]

        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, game_over):
        '''
        Store every play_step in self.memory
        '''
        self.memory.append((state, action, reward, next_state, game_over))

    def train_long_memory(self):
        '''
        Train memory after run is complete (snake dies) with random sample of BATCH_SIZE
        '''
        if len(self.memory) > BATCH_SIZE:
            sample = random.sample(self.memory, BATCH_SIZE) # returns list of tuples
        else:
            sample = self.memory
        states, actions, rewards, next_states, game_overs = zip(*sample)
        
        self.trainer.train_step(states, actions, rewards, next_states, game_overs)

    def train_short_memory(self, state, action, reward, next_state, game_over):
        '''
        Train model with each play_step the snake takes (every time the snake moves)
        '''
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
            prediction = self.model(tensor_state) # this is how you predict with pytorch (will automatically execute model.forward()
            dir = torch.argmax(prediction).item()
            move[dir] = 1

        return move

def train():
    '''
    Main function for training snake AI. Total 6 Steps:
    1. Get Old State
    2. Get the next action
    3. Apply action to game and get new state of snake
    4. Train short memory
    5. Store play_step in memory
    6. If done, train long memory (based on entire runs), plot, and repeat 
    '''
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
                agent.model.save()
            print('Game:', agent.num_games, ', Score:', score, ', Record:', record)

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.num_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)

if __name__ == '__main__':
    train()
