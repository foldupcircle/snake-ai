import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

pygame.init()
font = pygame.font.Font('arial.ttf', 25)

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4
    
Point = namedtuple('Point', 'x, y')

# rgb colors
WHITE = (255, 255, 255)
RED = (200,0,0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)

BLOCK_SIZE = 20
SPEED = 20

class SnakeGameAI:
    
    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()
        self.reset()
    
    def reset(self, level=0):
        # init game state
        self.direction = Direction.RIGHT
        
        self.head = Point(self.w/2, self.h/2)
        self.snake = [
            self.head, 
            Point(self.head.x - BLOCK_SIZE, self.head.y),
            Point(self.head.x - (2 * BLOCK_SIZE), self.head.y)
        ]
        
        self.score = 0
        self.food = None
        self._place_food(level)
        self.frame_iteration = 0
        self.obstacles = []
        
    def find_obstacles(self):
        head = self.snake[0]

        # straight
        temp_pt = Point(head.x, head.y)
        straight_count = 0
        while not self.is_collision(temp_pt):
            straight_count += 1
            new_x, new_y = self._next_pt_in_direction(temp_pt.x, temp_pt.y, 'straight')
            temp_pt = Point(new_x, new_y)

        # left
        temp_pt = Point(head.x, head.y)
        left_count = 0
        while not self.is_collision(temp_pt):
            left_count += 1
            new_x, new_y = self._next_pt_in_direction(temp_pt.x, temp_pt.y, 'left')
            temp_pt = Point(new_x, new_y)

        # right
        temp_pt = Point(head.x, head.y)
        right_count = 0
        while not self.is_collision(temp_pt):
            right_count += 1
            new_x, new_y = self._next_pt_in_direction(temp_pt.x, temp_pt.y, 'right')
            temp_pt = Point(new_x, new_y)

        return straight_count, left_count, right_count
        
    def _next_pt_in_direction(self, x, y, direction: str):
        direction_circle = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        index = direction_circle.index(self.direction)
        if direction == 'straight':
            new_dir = direction_circle[index % 4]
        elif direction == 'right':
            new_dir = direction_circle[(index + 1) % 4]
        elif direction == 'left':
            new_dir = direction_circle[(index - 1) % 4]

        if new_dir == Direction.LEFT:
            x -= 20
        elif new_dir == Direction.RIGHT:
            x += 20
        elif new_dir == Direction.UP:
            y -= 20
        elif new_dir == Direction.DOWN:
            y += 20
        
        return x, y

    def _add_obstacles(self, num_obstacles=0):
        obstacles_added = 0
        while obstacles_added != num_obstacles:
            x = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE 
            y = random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            if self._space_avail(x, y):
                obstacles_added += 1
                self.obstacles.append(Point(x, y))


    def _space_avail(self, x, y):
        if self.food.x == x and self.food.y == y:
            return False

        for s in self.snake:
            if s.x == x and s.y == y:
                return False
        
        return True
        
    def _place_food(self, level):
        if level == 0:
            num_obstacles = self.score // 3
        else:
            num_obstacles = (level - 1) * 5
        x = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE ) * BLOCK_SIZE 
        y = random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE ) * BLOCK_SIZE
        self.food = Point(x, y)
        self.obstacles = []
        self._add_obstacles(num_obstacles)
        if self.food in self.snake:
            self._place_food(level)
        
    def play_step(self, action, level=0):
        self.frame_iteration += 1

        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        # 2. move
        self._move(action) # update the head
        self.snake.insert(0, self.head)
        
        # 3. check if game over
        reward = 0
        game_over = False
        if self.is_collision() or self.frame_iteration > (100 * len(self.snake)):
            game_over = True
            reward = -10
            return reward, game_over, self.score
        
        # 4. place new food or just move
        if self.head == self.food:
            self.score += 1
            reward = 10
            self._place_food(level)
        else:
            self.snake.pop()
        
        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)
        
        # 6. return game over and score
        return reward, game_over, self.score
    
    def is_collision(self, pt=None):
        if pt is None:
            pt = self.head

        # hits boundary
        if pt.x > self.w - BLOCK_SIZE or pt.x < 0 or pt.y > self.h - BLOCK_SIZE or pt.y < 0:
            return True
            
        # hits itself
        if pt in self.snake[1:]:
            return True
        
        # hits obstacle
        if pt in self.obstacles:
            return True
        
        return False
        
    def _update_ui(self):
        self.display.fill(BLACK)
        
        # add all the snake blocks
        for pt in self.snake:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x + 4, pt.y + 4, 12, 12))

        # add the food blocks
        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))
        
        # add obstacles
        for ob in self.obstacles:
            pygame.draw.rect(self.display, GRAY, pygame.Rect(ob.x, ob.y, BLOCK_SIZE, BLOCK_SIZE))

        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()
        
    def _move(self, action):
        # action: [straight, right, left]

        direction_circle = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        index = direction_circle.index(self.direction)
        if np.array_equal(action, [1, 0, 0]):
            new_dir = direction_circle[index]
        elif np.array_equal(action, [0, 1, 0]):
            new_dir = direction_circle[(index + 1) % 4]
        elif np.array_equal(action, [0, 0, 1]):
            new_dir = direction_circle[(index - 1) % 4]
        self.direction = new_dir

        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE
            
        self.head = Point(x, y)
