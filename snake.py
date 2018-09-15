#!/usr/bin/python
# -*-coding: utf-8 -*-

import itertools
import pygame
import random
import sys
import time
from dataclasses import dataclass
from pygame.locals import *
from collections import deque

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
DARKGRAY = (40, 40, 40)


@dataclass
class Item:
    window_width: int = 320
    window_height: int = 320
    cell_size: int = 20

    cell_width = int(window_width / cell_size)
    cell_height = int(window_height / cell_size)


class Apple(Item):
    def __init__(self):
        self.location = None

    def refresh(self, snake):
        available_position = (
            set(itertools.product(range(self.cell_width - 1), range(self.cell_height - 1))) - set(snake.body)
        )
        try:
            location = random.sample(available_position, 1)[0]
        except ValueError:
            location = None
        self.location = location


def flattener(l):
    return [item for sublist in l for item in sublist]


class Snake(Item):
    def __init__(self, initial_length: int = 3, direction: str = 'right'):
        """
        :param initial_length: The initial length of the snake
        :param direction: Snake's default direction
        """
        self.initial_length = initial_length
        self.direction = direction

        # TODO: start from the middle instead
        if not 0 < initial_length < self.cell_width:
            raise ValueError(f"Initial_length should fall in (0, {self.cell_width})")
        start_x = random.randint(initial_length + 2, self.cell_width - (initial_length + 3))
        start_y = random.randint(initial_length + 2, self.cell_height - (initial_length + 3))

        self.body = list(zip([start_x] * initial_length, range(start_y, start_y - initial_length, -1)))
        self.score = 0
        self.is_dead = False
        self.eaten = False

    def get_head(self):
        return self.body[-1]

    def cheak_dead(self):
        """
        Check if the snake is dead, update the result in self.is_dead and return it as well
        :return: Boolean
        """
        dead = False
        x, y = self.get_head()
        if not 0 <= x < self.cell_width or not 0 <= y < self.cell_height or self.get_head() in self.body[:-1]:
            dead = True
        self.is_dead = dead
        return dead

    # TODO: replace check_dead with new_check_dead
    def new_check_dead(self, head, body):
        dead = False
        x, y = head
        if not 0 <= x < self.cell_width or not 0 <= y < self.cell_height or head in body[:-1]:
            dead = True
        return dead

    def cut_tail(self):
        self.body.pop(0)

    # TODO: make it accept next point instead of direction
    def grow(self):
        x, y = self.get_head()
        if self.direction == 'up':
            y -= 1
        elif self.direction == 'down':
            y += 1
        elif self.direction == 'left':
            x -= 1
        elif self.direction == 'right':
            x += 1
        self.body.append((x, y))

    def move(self, apple, direction=None):
        """
        Given the location of apple, decide if the apple is eaten (same location as the snake's head)
        :param apple: Apple instance
        :param direction: Optional. If direction is None, use snake's default or previous direction.
        :return: Boolean. Whether the apple is eaten.
        """
        # Pass in direction through parameter
        if direction:
            self.direction = direction

        # make the move
        self.grow()

        if self.cheak_dead():
            return

        # if the snake eats the apple, score adds 1
        if self.get_head() == apple.location:
            self.eaten = True
            self.score += 1
        # Otherwise, cut the tail so that snake moves forward without growing
        else:
            self.eaten = False
            self.cut_tail()

class BFS(Snake):
    def __init__(self,snake,apple):
        """
        :param body:
        :param apple:
        """
        super().__init__()
        self.snake=snake
        self.apple=apple

    def run(self):
        queue=deque([])
        queue.append([self.snake.get_head()])
        while queue:
            path=queue.popleft()
            node=path[-1]
            # print(node)
            # print(self.apple.location)

            if node == self.apple.location:
                first_node_x, first_node_y = path[0]
                second_node_x, second_node_y = path[1]
                if first_node_x - second_node_x == 1:
                    direction = "left"
                elif first_node_x - second_node_x == -1:
                    direction = 'right'
                elif first_node_y - second_node_y == 1:
                    direction = 'up'
                elif first_node_y - second_node_y == -1:
                    direction = 'down'
                else:
                    direction = 'right'
                #return path
                return direction

            # TODO: make BFS and snake returning location of next point, instead of direction
            for diff in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                diff_x, diff_y = diff
                node_x, node_y = node
                new_node_x = node_x+diff_x
                new_node_y = node_y+diff_y

                if self.new_check_dead(head=(new_node_x,new_node_y), body=self.snake.body):
                    continue
                if  (new_node_x,new_node_y) in flattener(queue):
                    continue
                new_path = list(path)
                new_path.append((new_node_x,new_node_y))
                queue.append(new_path)

@dataclass
class SnakeGame(Item):
    fps: int = 30

    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.display = pygame.display.set_mode((self.window_width, self.window_height))
        self.basic_font = pygame.font.Font('freesansbold.ttf', 18)
        pygame.display.set_caption('Perfect Snake')

        self.cell_width = int(self.window_width / self.cell_size)
        self.cell_height = int(self.window_height / self.cell_size)

    def launch(self):
        while True:
            self.game()
            # self.showGameOverScreen()
            self.pause_game()
            print('loop')

    def game(self):
        snake = Snake()

        apple = Apple()
        apple.refresh(snake=snake)

        count = 0

        while True:  # main game loop
            count += 1
            bfs = BFS(snake=snake,apple=apple)
            snake.direction =bfs.run()
            # TODO: if BFS has no result, it should wonder
            # for event in pygame.event.get():  # event handling loop
            #     if event.type == QUIT:
            #         self.terminate()
            #
                # TODO: add Player class, which accepts snake and apple, cache the location and outputs the direction
                # elif event.type == KEYDOWN:
                #     if (event.key == K_LEFT or event.key == K_a) and snake.direction != 'right':
                #         snake.direction = 'left'
                #     elif (event.key == K_RIGHT or event.key == K_d) and snake.direction != 'left':
                #         snake.direction = 'right'
                #     elif (event.key == K_UP or event.key == K_w) and snake.direction != 'down':
                #         snake.direction = 'up'
                #     elif (event.key == K_DOWN or event.key == K_s) and snake.direction != 'up':
                #         snake.direction = 'down'
                #     elif event.key == K_ESCAPE:
                #         self.terminate()

            # if count >= 10:
            #     break



            snake.move(apple=apple)

            if snake.is_dead:
                break
            elif snake.eaten:
                apple.refresh(snake=snake)

            self.display.fill(BLACK)
            self.draw_panel()
            self.draw_snake(snake.body)

            self.draw_apple(apple.location)
            pygame.display.update()
            self.clock.tick(self.fps)

        print(snake.score)

    @staticmethod
    def terminate():
        pygame.quit()
        sys.exit()

    def pause_game(self):
        while True:
            time.sleep(0.2)
            for event in pygame.event.get():  # event handling loop
                if event.type == QUIT:
                    self.terminate()
                if event.type == KEYUP:
                    if event.key == K_ESCAPE:
                        self.terminate()
                    else:
                        return

    def draw_snake(self, snake_body):
        for snake_block_x, snake_block_y in snake_body:
            x = snake_block_x * self.cell_size
            y = snake_block_y * self.cell_size
            snake_block = pygame.Rect(x, y, self.cell_size, self.cell_size)
            pygame.draw.rect(self.display, WHITE, snake_block)

    def draw_apple(self, apple_location):
        apple_x, apple_y = apple_location
        apple_block = pygame.Rect(apple_x * self.cell_size, apple_y * self.cell_size, self.cell_size, self.cell_size)
        pygame.draw.rect(self.display, RED, apple_block)

    def draw_panel(self):
        for x in range(0, self.window_width, self.cell_size):  # draw vertical lines
            pygame.draw.line(self.display, DARKGRAY, (x, 0), (x, self.window_height))
        for y in range(0, self.window_height, self.cell_size):  # draw horizontal lines
            pygame.draw.line(self.display, DARKGRAY, (0, y), (self.window_width, y))


if __name__ == '__main__':
    SnakeGame().launch()