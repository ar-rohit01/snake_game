import rclpy
from rclpy.node import Node
import numpy as np
import matplotlib.pyplot as plt
import random

GRID_SIZE = 10

class SnakeGame(Node):
    def __init__(self):
        super().__init__('snake_game')
        self.grid_size = GRID_SIZE
        self.snake = [(5, 5)]
        self.food = self.spawn_food()
        self.timer = self.create_timer(0.3, self.game_loop)

        # Matplotlib visualization
        plt.ion()
        self.fig, self.ax = plt.subplots()
        self.im = self.ax.imshow(self.render(), cmap='viridis', vmin=0, vmax=3)
        self.ax.set_title("Snake Game")

    def spawn_food(self):
        while True:
            f = (random.randint(0, self.grid_size - 1), random.randint(0, self.grid_size - 1))
            if f not in self.snake:
                return f

    def render(self):
        grid = np.zeros((self.grid_size, self.grid_size))
        for x, y in self.snake:
            grid[self.grid_size - 1 - y][x] = 1  # Snake body
        fx, fy = self.food
        grid[self.grid_size - 1 - fy][fx] = 2  # Food
        return grid

    def game_loop(self):
        head_x, head_y = self.snake[0]
        food_x, food_y = self.food

        # Determine direction towards food (horizontal priority)
        dx, dy = 0, 0
        if head_x < food_x:
            dx = 1
        elif head_x > food_x:
            dx = -1
        elif head_y < food_y:
            dy = 1
        elif head_y > food_y:
            dy = -1

        new_head = (head_x + dx, head_y + dy)
        self.get_logger().info(f"Head: {new_head}, Food: {self.food}")

        # Collision checks
        if (
            new_head in self.snake or
            not (0 <= new_head[0] < self.grid_size and 0 <= new_head[1] < self.grid_size)
        ):
            self.get_logger().info("Game Over! Collision detected.")
            rclpy.shutdown()
            plt.close(self.fig)
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.get_logger().info("Food eaten!")
            self.food = self.spawn_food()
        else:
            self.snake.pop()

        self.im.set_data(self.render())
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        plt.pause(0.01)

def main(args=None):
    rclpy.init(args=args)
    node = SnakeGame()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
