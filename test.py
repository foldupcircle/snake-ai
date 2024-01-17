import os
from game import SnakeGameAI
from agent import Agent
import torch
import os

def test(level=1):
    '''
    Tests the snake with the option for the user to select levels.
    Difficulty is easiest in Level 1 where there is no obstacles to the hardest in Level 5 (20 obstacles)
    '''
    agent = Agent()
    game = SnakeGameAI()
    file_path = os.path.join('./model', 'model_obstacles2.pth')
    agent.model.load_state_dict(torch.load(file_path))
    agent.model.eval()
    agent.num_games = 100
    while True:
        # get old state
        old_state = agent.get_state(game) 

        # get the next action based on the model
        next_action = agent.get_action(old_state) 

        # apply move to game and get the new state
        reward, done, score = game.play_step(next_action, level)
        new_state = agent.get_state(game)

        # remember
        agent.remember(old_state, next_action, reward, new_state, done)

        if done:
            game.reset(level)
            print('Level:', level, ', Score:', score)
            break

if __name__ == '__main__':
    level = input("Level (1-5): ") 
    assert level.isdigit()
    assert int(level) <= 5 and int(level) >= 1
    test(int(level))
