import copy

import lib.stddraw as stddraw  # used for displaying the game grid
from lib.color import Color  # used for coloring the game grid
from point import Point  # used for tile positions
import numpy as np  # fundamental Python module for scientific computing

from tetromino import Tetromino
from tile import Tile
from random import choice


# A class for modeling the game grid
def get_next_display_dict(grid_width):
    pass


class GameGrid:
    # A constructor for creating the game grid based on the given arguments
    def __init__(self, grid_h, grid_w):
        # set the dimensions of the game grid as the given arguments
        self.grid_height = grid_h
        self.grid_width = grid_w
        # create a tile matrix to store the tiles locked on the game grid
        self.tile_matrix = np.full((grid_h, grid_w), None)
        # create the tetromino that is currently being moved on the game grid
        self.current_tetromino = None
        # create the tetromino that will enter the game grid next
        # the game_over flag shows whether the game is over or not
        self.game_over = False
        # set the color used for the empty grid cells
        self.empty_cell_color = Color(206, 195, 181)
        # set the colors used for the grid lines and the grid boundaries
        self.line_color = Color(185, 171, 158)
        self.boundary_color = Color(132, 122, 113)
        # thickness values used for the grid lines and the grid boundaries
        self.line_thickness = 0.002
        self.box_thickness = 10 * self.line_thickness
        # the score of the game starts from 0
        self.score = 0

    # A method for displaying the game grid
    def display(self, next_tetromino):
        # clear the background to empty_cell_color
        stddraw.clear(self.empty_cell_color)
        # draw the game grid
        self.draw_grid()
        # draw the current/active tetromino if it is not None
        # (the case when the game grid is updated)
        if self.current_tetromino is not None:
            self.current_tetromino.draw()
        # draw a box around the game grid
        self.draw_boundaries()
        # show the resulting drawing with a pause duration = 250 ms
        self.score = Tile.merge_tiles(self.tile_matrix, self.score)

        self.remove_floating_tetrominos()

        self.display_next_tetromino(next_tetromino)

    def display_score(self):
        stddraw.setFontSize(28)
        stddraw.setPenColor(Color(69, 60, 51))
        stddraw.text(self.grid_width + 1.5, self.grid_height - 17.5, "Score")
        stddraw.setFontFamily("Arial")
        stddraw.text(self.grid_width + 1.5, self.grid_height - 18 - 0.8, str(self.score))
        stddraw.setFontFamily("Arial")
        stddraw.setFontSize(22)
        stddraw.text(self.grid_width + 1.60, self.grid_height - 2, "Next Tetromino")

    # A method for drawing the cells and the lines of the game grid
    def draw_grid(self):
        # for each cell of the game grid
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                # if the current grid cell is occupied by a tile
                if self.tile_matrix[row][col] is not None:
                    # draw this tile
                    self.tile_matrix[row][col].draw(Point(col, row))
        # draw the inner lines of the game grid
        stddraw.setPenColor(self.line_color)
        stddraw.setPenRadius(self.line_thickness)
        # x and y ranges for the game grid
        start_x, end_x = -0.5, self.grid_width - 0.5
        start_y, end_y = -0.5, self.grid_height - 0.5
        for x in np.arange(start_x + 1, end_x, 1):  # vertical inner lines
            stddraw.line(x, start_y, x, end_y)
        for y in np.arange(start_y + 1, end_y, 1):  # horizontal inner lines
            stddraw.line(start_x, y, end_x, y)
        stddraw.setPenRadius()  # reset the pen radius to its default value
        self.display_score()

    # A method for drawing the boundaries around the game grid
    def draw_boundaries(self):
        # draw a bounding box around the game grid as a rectangle
        stddraw.setPenColor(self.boundary_color)  # using boundary_color
        # set the pen radius as box_thickness (half of this thickness is visible
        # for the bounding box as its lines lie on the boundaries of the canvas)
        stddraw.setPenRadius(self.box_thickness)
        # the coordinates of the bottom left corner of the game grid
        pos_x, pos_y = -0.5, -0.5
        stddraw.rectangle(pos_x, pos_y, self.grid_width, self.grid_height)
        stddraw.setPenRadius()  # reset the pen radius to its default value

    # A method used checking whether the grid cell with the given row and column
    # indexes is occupied by a tile or not (i.e., empty)
    def is_occupied(self, row, col):
        # considering the newly entered tetrominoes to the game grid that may
        # have tiles with position.y >= grid_height
        if not self.is_inside(row, col):
            return False  # the cell is not occupied as it is outside the grid
        # the cell is occupied by a tile if it is not None
        return self.tile_matrix[row][col] is not None

    # A method for checking whether the cell with the given row and col indexes
    # is inside the game grid or not
    def is_inside(self, row, col):
        if row < 0 or row >= self.grid_height:
            return False
        if col < 0 or col >= self.grid_width:
            return False
        return True

    # A method that locks the tiles of a landed tetromino on the grid checking
    # if the game is over due to having any tile above the topmost grid row.
    # (This method returns True when the game is over and False otherwise.)
    def update_grid(self, tiles_to_lock, blc_position):
        # necessary for the display method to stop displaying the tetromino
        self.current_tetromino = None
        # lock the tiles of the current tetromino (tiles_to_lock) on the grid
        n_rows, n_cols = len(tiles_to_lock), len(tiles_to_lock[0])
        for col in range(n_cols):
            for row in range(n_rows):
                # place each tile (occupied cell) onto the game grid
                if tiles_to_lock[row][col] is not None:
                    # compute the position of the tile on the game grid
                    pos = Point()
                    pos.x = blc_position.x + col
                    pos.y = blc_position.y + (n_rows - 1) - row
                    if self.is_inside(pos.y, pos.x):
                        self.tile_matrix[pos.y][pos.x] = tiles_to_lock[row][col]
                    # the game is over if any placed tile is above the game grid
                    else:
                        self.game_over = True
        # return the value of the game_over flag
        return self.game_over

    # A method for removing the full rows from the game grid and updating the
    # game grid by shifting down the tiles above the removed rows
    def remove_full_rows(self):
        # the list of full rows to be removed from the game grid
        full_rows = []
        # check each row of the game grid for being full
        for row in range(self.grid_height):
            # check if the current row is full
            if self.is_full(row):
                full_rows.append(row)
        # remove the full rows from the game grid
        for row in reversed(full_rows):
            self.remove_row(row)
        # return the number of full rows removed from the game grid
        return len(full_rows)

    # A method for checking whether the given row is full or not
    def is_full(self, row):
        # check if there is any empty cell in the given row
        for col in range(self.grid_width):
            if self.tile_matrix[row][col] is None:
                return False
        return True

    # A method for removing the given row from the game grid
    def remove_row(self, row):

        self.calculate_score(row)
        # remove the given row from the game grid
        for r in range(row, self.grid_height - 1):
            for col in range(self.grid_width):
                self.tile_matrix[r][col] = self.tile_matrix[r + 1][col]
        for col in range(self.grid_width):
            self.tile_matrix[self.grid_height - 1][col] = None

    # A method for calculating the score when deleting a row
    def calculate_score(self, row):
        # iterate over the tiles in the row
        for col in range(self.grid_width):
            tile = self.tile_matrix[row][col]
            if tile is not None:
                # add the number in the tile to the score
                self.score += tile.number

    def reset(self):
        # Set all tiles in the grid to None
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                self.tile_matrix[row][col] = None

        # Reset the score
        self.score = 0

        self.current_tetromino = None


    def display_next_tetromino(self, next_tetromino):
        # Define the position where the next Tetromino will be displayed
        display_position = Point(self.grid_width + 0.75, self.grid_height - 4)

        # Iterate over the tiles of the next Tetromino
        for row in range(next_tetromino.tile_matrix.shape[0]):
            for col in range(next_tetromino.tile_matrix.shape[1]):
                tile = next_tetromino.tile_matrix[row, col]
                if tile is not None:
                    # Calculate the position of the tile on the game grid
                    pos = Point()
                    pos.x = display_position.x + col
                    pos.y = display_position.y - row
                    # Draw the tile
                    tile.draw(pos)

    def remove_floating_tetrominos(self):
        temp_score = 0
        # Create a set to store the positions of all connected cells
        connected = set()
        # Perform a DFS from each cell at the bottom of the grid
        for col in range(self.grid_width):
            if self.tile_matrix[0][col] is not None:
                self.dfs(0, col, connected)
        # Iterate over the entire grid
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                # If a cell is not connected, it's floating
                if self.tile_matrix[row][col] is not None and (row, col) not in connected:
                    temp_score += self.tile_matrix[row][col].number
                    self.tile_matrix[row][col] = None
        self.score += temp_score

    def dfs(self, row, col, connected):
        # If the cell is outside the grid or already visited, return
        if row < 0 or row >= self.grid_height or col < 0 or col >= self.grid_width or (row, col) in connected:
            return
        # If the cell is empty, return
        if self.tile_matrix[row][col] is None:
            return
        # Mark the cell as connected
        connected.add((row, col))
        # Visit all adjacent cells
        self.dfs(row + 1, col, connected)
        self.dfs(row - 1, col, connected)
        self.dfs(row, col + 1, connected)
        self.dfs(row, col - 1, connected)