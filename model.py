import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import os

class Linear_QNet(nn.Module):
    def __init__(self, input_size, hidden_size, output_size) -> None:
        super().__init__()
        self.linear1 = nn.Linear(input_size, hidden_size) # this is how to define layers using pytorch
        self.linear2 = nn.Linear(hidden_size, output_size)
    
    def forward(self, x):
        x = F.relu(self.linear1(x)) # Relu is activation function, what is it exactly, why does this work?
        x = self.linear2(x) # why not relu here?
        return x

    def save(self, file_name='model.pth'): # saving whatever model we have into our folders
        model_folder_path = './model'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)

        file_name = os.path.join(model_folder_path, file_name)
        torch.save(self.state_dict(), file_name)
    
class QTrainer:
    def __init__(self, model, learning_rate, gamma) -> None:
        self.learning_rate = learning_rate # what role does learning rate have in equations and overall result?
        self.gamma = gamma # what role exactly does gamma have in the equations and overall result?
        self.model = model
        self.optim = optim.Adam(model.parameters(), lr=self.learning_rate) # what does the optimizer do exactly?
        self.criterion = nn.MSELoss() # (Q_new - Q)^2 = MSE_loss - what exactly is Q and why is it defined in the way it is?

    def train_step(self, old_state, action, reward, new_state, game_over):
        state = torch.tensor(old_state, dtype=torch.float)
        next_state = torch.tensor(new_state, dtype=torch.float)
        action = torch.tensor(action, dtype=torch.long)
        reward = torch.tensor(reward, dtype=torch.float)

        if len(state.shape) == 1:
            state = torch.unsqueeze(state, 0)
            next_state = torch.unsqueeze(next_state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            game_over = (game_over, )

        # BELLMAN EQUATION and Q UPDATE RULE

        pred = self.model(state)
        target = pred.clone() # why are we cloning?
        for i in range(len(game_over)):
            Q_new = reward[i]
            if not game_over[i]:
                Q_new = reward[i] + (self.gamma * torch.max(self.model(next_state[i]))) # applying the Q update rule
            target[i][torch.argmax(action).item()] = Q_new # I don't understand the torch.argmax part

        self.optim.zero_grad() # why do we have to do this?
        loss = self.criterion(target, pred) # what does MSEloss return - this returns the mean squared loss
        loss.backward() # how does back_prop work exactly?

        self.optim.step() # stepping with the optimizer? Maybe like mpc, look into how this works

