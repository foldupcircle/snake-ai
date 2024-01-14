from game import SnakeGameAI
from agent import Agent
from helper import plot
import torch

def test(level=1):
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = SnakeGameAI()
    agent.model = torch.load()
    while True:
        # get old state
        old_state = agent.get_state(game) 

        # get the next action based on the model
        next_action = agent.get_action(old_state) 

        # apply move to game and get the new state
        reward, done, score = game.play_step(next_action)
        new_state = agent.get_state(game)

        # remember
        agent.remember(old_state, next_action, reward, new_state, done)

        if done:
            # train long memory
            game.reset()
            if score > record:
                record = score
            print('Level:', level, ', Score:', score, ', Record:', record)

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.num_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)



if __name__ == '__main__':
    level = input("Level (1-5): ") 
    assert level.isdigit()
    assert int(level) <= 5 and int(level) >= 1
    print(level)
    test(int(level))
